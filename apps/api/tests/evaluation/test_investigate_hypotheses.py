import pytest
from unittest.mock import patch, MagicMock

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    Observation,
)
from app.features.investigation.schema import EvidenceReference
from app.features.investigation.agents.investigate_hypotheses import (
    investigate_hypotheses_node,
    InvestigateHypothesesResult,
    InvestigatedHypothesis,
)

@pytest.fixture
def base_state() -> MultiAgentInvestigationState:
    return {
        "investigation_id": "123",
        "incident_id": "456",
        "incident_context": {"title": "Test Incident"},
        "evidence_payload": [
            {"id": "ev-1", "filename": "db.log", "content": "timeout"},
            {"id": "ev-2", "filename": "app.log", "content": "error"}
        ],
        "timeline": [],
        "observations": [
            Observation(description="Timeout seen", evidence_id="ev-1", timeline_event_ids=[10])
        ],
        "hypotheses": [],
        "validation_findings": [],
        "ranking": [],
        "recommendations": None,
        "summary": None,
        "errors": [],
        "warnings": []
    }

@patch("app.features.investigation.agents.investigate_hypotheses.ChatPromptTemplate")
@patch("app.features.investigation.agents.investigate_hypotheses.BoundedChatOllama")
def test_valid_investigation(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = InvestigateHypothesesResult(
        hypotheses=[
            InvestigatedHypothesis(
                id="H1",
                hypothesis="DB Timeout",
                reasoning="Logs",
                supporting_evidence=["ev-1"],
                contradicting_evidence=[],
                missing_evidence=[],
                immediate_mitigations=["Restart"],
                preventative_measures=["Scale"],
                is_valid=True
            )
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = investigate_hypotheses_node(base_state)
    
    assert "hypotheses" in result
    assert "validation_findings" in result
    assert "errors" not in result
    
    assert len(result["hypotheses"]) == 1
    assert result["hypotheses"][0].id == "H1"
    
    assert len(result["validation_findings"]) == 1
    assert result["validation_findings"][0].hypothesis_id == "H1"
    assert result["validation_findings"][0].is_valid is True

    # Verify context optimization: timeline should not be sent
    mock_chain.invoke.assert_called_once()
    call_args = mock_chain.invoke.call_args[0][0]
    
    assert "incident_context" in call_args
    assert "observations" in call_args
    assert "timeline" not in call_args

@patch("app.features.investigation.agents.investigate_hypotheses.ChatPromptTemplate")
@patch("app.features.investigation.agents.investigate_hypotheses.BoundedChatOllama")
def test_invalid_evidence_reference(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = InvestigateHypothesesResult(
        hypotheses=[
            InvestigatedHypothesis(
                id="H1",
                hypothesis="DB Timeout",
                reasoning="Logs",
                supporting_evidence=["ev-fake"],
                contradicting_evidence=[],
                missing_evidence=[],
                immediate_mitigations=["Restart"],
                preventative_measures=["Scale"],
                is_valid=True
            )
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = investigate_hypotheses_node(base_state)
    
    assert "hypotheses" in result
    assert "validation_findings" in result
    assert "warnings" in result
    assert len(result["hypotheses"][0].supporting_evidence) == 0
    assert any("hallucinated evidence_id" in warn for warn in result["warnings"])

@patch("app.features.investigation.agents.investigate_hypotheses.ChatPromptTemplate")
@patch("app.features.investigation.agents.investigate_hypotheses.BoundedChatOllama")
def test_partial_invalid_evidence_reference(mock_ollama, mock_prompt, base_state):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = InvestigateHypothesesResult(
        hypotheses=[
            InvestigatedHypothesis(
                id="H1",
                hypothesis="DB Timeout",
                reasoning="Logs",
                supporting_evidence=["ev-1", "ev-fake"],
                contradicting_evidence=[],
                missing_evidence=[],
                immediate_mitigations=["Restart"],
                preventative_measures=["Scale"],
                is_valid=True
            )
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = investigate_hypotheses_node(base_state)
    
    assert "hypotheses" in result
    assert "validation_findings" in result
    assert "warnings" in result
    
    # ev-1 should be kept, ev-fake should be filtered out
    supporting = result["hypotheses"][0].supporting_evidence
    assert len(supporting) == 1
    assert supporting[0].evidence_id == "ev-1"
    
    assert any("hallucinated evidence_id 'ev-fake'" in warn for warn in result["warnings"])

def test_empty_observations():
    empty_state = {
        "observations": []
    }
    result = investigate_hypotheses_node(empty_state)
    assert "errors" in result
    assert result["errors"] == ["Cannot generate hypotheses: No observations provided."]

@patch("app.features.investigation.agents.investigate_hypotheses.ChatPromptTemplate")
@patch("app.features.investigation.agents.investigate_hypotheses.BoundedChatOllama")
def test_deterministic_downgrade_missing_evidence(mock_ollama, mock_prompt, base_state):
    """
    Ensures that an unverified deployment misconfiguration (or any missing evidence)
    deterministically forces is_valid to False even if the LLM claims True.
    """
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = InvestigateHypothesesResult(
        hypotheses=[
            InvestigatedHypothesis(
                id="H2",
                hypothesis="Connection pool exhausted due to new deployment",
                reasoning="Logs show exhaustion.",
                supporting_evidence=["ev-1"],
                contradicting_evidence=[],
                missing_evidence=["Deployment records proving a config change"],
                immediate_mitigations=["Restart"],
                preventative_measures=["Fix config"],
                is_valid=True # LLM mistakenly thinks it's valid
            )
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = investigate_hypotheses_node(base_state)
    
    assert "hypotheses" in result
    assert "validation_findings" in result
    
    # Check that is_valid was deterministically downgraded
    finding = result["validation_findings"][0]
    assert finding.is_valid is False
    assert "Deterministically downgraded" in finding.uncertainty_rationale

@patch("app.features.investigation.agents.investigate_hypotheses.ChatPromptTemplate")
@patch("app.features.investigation.agents.investigate_hypotheses.BoundedChatOllama")
def test_hallucinated_evidence_format(mock_ollama, mock_prompt, base_state):
    """
    Ensures that if the LLM returns descriptive strings instead of IDs,
    it is caught by the validation check.
    """
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = InvestigateHypothesesResult(
        hypotheses=[
            InvestigatedHypothesis(
                id="H3",
                hypothesis="DB Timeout",
                reasoning="Logs",
                supporting_evidence=["database connection timeout (18:20:05)"],
                contradicting_evidence=[],
                missing_evidence=[],
                immediate_mitigations=["Restart"],
                preventative_measures=["Scale"],
                is_valid=True
            )
        ]
    )
    mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

    result = investigate_hypotheses_node(base_state)
    
    assert "hypotheses" in result
    assert "warnings" in result
    assert len(result["hypotheses"][0].supporting_evidence) == 0
    assert any("hallucinated evidence_id 'database connection timeout (18:20:05)'" in warn for warn in result["warnings"])
