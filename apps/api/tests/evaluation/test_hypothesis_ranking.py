import pytest

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    MultiAgentHypothesis,
    ValidationFinding,
)
from app.features.investigation.schema import EvidenceReference
from app.features.investigation.agents.hypothesis_ranking import rank_hypotheses_node

@pytest.fixture
def base_state() -> MultiAgentInvestigationState:
    h1 = MultiAgentHypothesis(
        id="H1", hypothesis="DB down", reasoning="Logs",
        supporting_evidence=[EvidenceReference(evidence_id="ev-1", filename="db.log", explanation="Timeout")],
        contradicting_evidence=[],
        missing_evidence=[],
        immediate_mitigations=["Restart"],
        preventative_measures=["Scale"]
    ) # Score: 110
    
    h2 = MultiAgentHypothesis(
        id="H2", hypothesis="Net issue", reasoning="Maybe",
        supporting_evidence=[],
        contradicting_evidence=[],
        missing_evidence=["Network logs"],
        immediate_mitigations=["Restart"],
        preventative_measures=["Scale"]
    ) # Score: 95
    
    v1 = ValidationFinding(
        hypothesis_id="H1", is_valid=True,
        contradicting_evidence=[], uncertainty_rationale=""
    ) # Score base + 100
    
    v2 = ValidationFinding(
        hypothesis_id="H2", is_valid=True,
        contradicting_evidence=[], uncertainty_rationale=""
    ) # Score base + 100
    
    return {
        "investigation_id": "123",
        "incident_id": "456",
        "incident_context": None,
        "evidence_payload": [],
        "timeline": [],
        "observations": [],
        "hypotheses": [h1, h2],
        "validation_findings": [v1, v2],
        "ranking": [],
        "recommendations": None,
        "summary": None,
        "errors": []
    }


def test_expected_ranking(base_state):
    result = rank_hypotheses_node(base_state)
    
    assert "ranking" in result
    ranks = result["ranking"]
    assert len(ranks) == 2
    assert ranks[0].hypothesis_id == "H1"
    assert ranks[0].rank == 1
    assert "Score: 110" in ranks[0].confidence_rationale
    
    assert ranks[1].hypothesis_id == "H2"
    assert ranks[1].rank == 2
    assert "Score: 95" in ranks[1].confidence_rationale
    assert "errors" not in result


def test_tied_scores_deterministic_ordering(base_state):
    # Make H3 and H4 identical in score
    h3 = MultiAgentHypothesis(
        id="H3", hypothesis="Tie 1", reasoning="",
        supporting_evidence=[], contradicting_evidence=[], missing_evidence=[],
        immediate_mitigations=[], preventative_measures=[]
    ) # Score: 100
    h4 = MultiAgentHypothesis(
        id="H4", hypothesis="Tie 2", reasoning="",
        supporting_evidence=[], contradicting_evidence=[], missing_evidence=[],
        immediate_mitigations=[], preventative_measures=[]
    ) # Score: 100
    v3 = ValidationFinding(hypothesis_id="H3", is_valid=True, contradicting_evidence=[], uncertainty_rationale="")
    v4 = ValidationFinding(hypothesis_id="H4", is_valid=True, contradicting_evidence=[], uncertainty_rationale="")
    
    base_state["hypotheses"] = [h4, h3] # Reverse insertion order
    base_state["validation_findings"] = [v4, v3]
    
    result = rank_hypotheses_node(base_state)
    ranks = result["ranking"]
    
    # H3 should beat H4 due to string sorting alphabetically ascending (-score, id)
    assert ranks[0].hypothesis_id == "H3"
    assert ranks[1].hypothesis_id == "H4"


def test_empty_hypotheses(base_state):
    base_state["hypotheses"] = []
    result = rank_hypotheses_node(base_state)
    assert "ranking" in result
    assert result["ranking"] == []


def test_invalid_hypothesis_reference(base_state):
    # H1 is missing validation finding
    base_state["validation_findings"] = [
        ValidationFinding(hypothesis_id="H2", is_valid=True, contradicting_evidence=[], uncertainty_rationale="")
    ]
    result = rank_hypotheses_node(base_state)
    
    assert "errors" in result
    assert "No validation finding for hypothesis 'H1'." in result["errors"][0]


def test_duplicate_hypothesis_ids(base_state):
    # Two H1s
    base_state["hypotheses"].append(base_state["hypotheses"][0])
    result = rank_hypotheses_node(base_state)
    
    assert "errors" in result
    assert "Duplicate hypothesis ID 'H1' detected." in result["errors"][0]
