import pytest

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    RecommendationResult,
    RankedHypothesis,
    MultiAgentHypothesis,
)
from app.features.investigation.agents.recommendation import generate_recommendations_node

@pytest.fixture
def base_state() -> MultiAgentInvestigationState:
    return {
        "investigation_id": "123",
        "incident_id": "456",
        "incident_context": None,
        "evidence_payload": [],
        "timeline": [],
        "observations": [],
        "hypotheses": [
            MultiAgentHypothesis(
                id="H-1", hypothesis="DB down", reasoning="",
                supporting_evidence=[], contradicting_evidence=[], missing_evidence=[],
                immediate_mitigations=["Restart DB"], preventative_measures=["Add scaling rules."]
            ),
            MultiAgentHypothesis(
                id="H-2", hypothesis="Network error", reasoning="",
                supporting_evidence=[], contradicting_evidence=[], missing_evidence=[],
                immediate_mitigations=["Check firewall"], preventative_measures=["Update rules"]
            )
        ],
        "validation_findings": [],
        "ranking": [
            RankedHypothesis(hypothesis_id="H-1", rank=1, confidence_rationale="Good"),
            RankedHypothesis(hypothesis_id="H-2", rank=2, confidence_rationale="Less Good")
        ],
        "recommendations": None,
        "summary": None,
        "errors": []
    }

def test_valid_recommendation_result(base_state):
    result = generate_recommendations_node(base_state)
    
    assert "recommendations" in result
    assert result["recommendations"].immediate_mitigations == ["Restart DB"]
    assert result["recommendations"].preventative_measures == ["Add scaling rules."]
    assert "errors" not in result

def test_empty_ranking():
    empty_state = {
        "ranking": []
    }
    result = generate_recommendations_node(empty_state)
    assert "recommendations" in result
    assert result["recommendations"].immediate_mitigations == ["No immediate mitigations could be generated."]

def test_empty_hypotheses(base_state):
    base_state["hypotheses"] = []
    result = generate_recommendations_node(base_state)
    assert "recommendations" in result
    assert result["recommendations"].preventative_measures == ["No preventative measures could be generated."]

def test_top_hypothesis_missing(base_state):
    base_state["ranking"] = [
        RankedHypothesis(hypothesis_id="H-MISSING", rank=1, confidence_rationale="")
    ]
    result = generate_recommendations_node(base_state)
    assert "errors" in result
    assert any("Top ranked hypothesis 'H-MISSING' not found" in err for err in result["errors"])
