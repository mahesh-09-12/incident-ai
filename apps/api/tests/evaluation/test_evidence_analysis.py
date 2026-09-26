import pytest
from unittest.mock import patch, MagicMock

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    Observation,
)
from app.features.investigation.timeline import TimelineEvent
from app.features.investigation.agents.evidence_analysis import (
    analyze_evidence_node,
    EvidenceAnalysisResult,
)
from datetime import datetime, timezone

@pytest.fixture
def base_state() -> MultiAgentInvestigationState:
    return {
        "investigation_id": "123",
        "incident_id": "456",
        "incident_context": None,
        "evidence_payload": [
            {"id": "ev-1", "filename": "db.log", "content": "timeout"}
        ],
        "timeline": [
            TimelineEvent(
                timestamp=datetime.now(timezone.utc),
                evidence_id="ev-1",
                filename="db.log",
                content="timeout",
                line_number=10
            )
        ],
        "observations": [],
        "hypotheses": [],
        "validation_findings": [],
        "ranking": [],
        "recommendations": None,
        "summary": None,
        "errors": []
    }


@patch("app.features.investigation.agents.evidence_analysis.ChatPromptTemplate")
@patch("app.features.investigation.agents.evidence_analysis.BoundedChatOllama")
def test_valid_structured_observations(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    # When chain.invoke is called, return our mock EvidenceAnalysisResult
    mock_chain.invoke.return_value = EvidenceAnalysisResult(
        observations=[
            Observation(description="Saw timeout", evidence_id="ev-1", timeline_event_ids=[10])
        ]
    )
    # prompt | llm syntax in python calls __or__ which we can mock on the prompt object
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = analyze_evidence_node(base_state)
    
    assert "observations" in result
    assert len(result["observations"]) == 1
    assert result["observations"][0].description == "Saw timeout"
    assert "errors" not in result

    # Verify context optimization
    mock_chain.invoke.assert_called_once()
    call_args = mock_chain.invoke.call_args[0][0]
    
    # Evidence should NOT have line numbers injected
    assert "[Line/Event ID: 1]" not in call_args["evidence"]
    assert "timeout" in call_args["evidence"]
    
    # Timeline should include the actual event content now
    assert "[10]" in call_args["timeline"]
    assert "(Source: ev-1)" in call_args["timeline"]
    assert ": timeout" in call_args["timeline"]


@patch("app.features.investigation.agents.evidence_analysis.ChatPromptTemplate")
@patch("app.features.investigation.agents.evidence_analysis.BoundedChatOllama")
def test_invalid_evidence_id(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = EvidenceAnalysisResult(
        observations=[
            Observation(description="Hallucination", evidence_id="ev-fake", timeline_event_ids=[10])
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = analyze_evidence_node(base_state)
    
    assert "observations" not in result
    assert "errors" in result
    assert any("Hallucinated evidence_id" in err for err in result["errors"])


@patch("app.features.investigation.agents.evidence_analysis.ChatPromptTemplate")
@patch("app.features.investigation.agents.evidence_analysis.BoundedChatOllama")
def test_invalid_timeline_id(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = EvidenceAnalysisResult(
        observations=[
            Observation(description="Bad timeline", evidence_id="ev-1", timeline_event_ids=[999])
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = analyze_evidence_node(base_state)
    
    assert "observations" not in result
    assert "errors" in result
    assert any("Hallucinated timeline_event_ids" in err for err in result["errors"])


def test_empty_evidence():
    empty_state = {
        "evidence_payload": []
    }
    result = analyze_evidence_node(empty_state)
    assert "errors" in result
    assert result["errors"] == ["No evidence provided for analysis."]


@patch("app.features.investigation.agents.evidence_analysis.ChatPromptTemplate")
@patch("app.features.investigation.agents.evidence_analysis.BoundedChatOllama")
def test_malformed_observation_structure(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    # Simulate a parsing exception from Langchain
    mock_chain.invoke.side_effect = Exception("OutputParserException")
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = analyze_evidence_node(base_state)
    
    assert "observations" not in result
    assert "errors" in result
    assert any("Failed to generate" in err for err in result["errors"])
