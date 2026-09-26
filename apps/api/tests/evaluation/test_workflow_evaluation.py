import pytest
import uuid
import json
from unittest.mock import patch, MagicMock

from app.features.investigation.schema import InvestigationAIResult, Hypothesis, EvidenceReference
from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    Observation,
    MultiAgentHypothesis,
    ValidationFinding,
    RankedHypothesis,
    RecommendationResult,
)
from app.features.investigation.multi_agent_workflow import finalize_result
from tests.evaluation.evaluator import evaluate_investigation

def mock_single_agent_success():
    """Mocks the output of the legacy workflow's single LLM call."""
    res = InvestigationAIResult(
        summary="DB incident",
        root_cause="DB overloaded",
        recommendations="Restart",
        supporting_evidence=[EvidenceReference(evidence_id="ev-1", filename="a", explanation="a")],
        contradicting_evidence=[],
        missing_evidence=[],
        hypotheses=[
            Hypothesis(
                id="H-1", hypothesis="DB overloaded", reasoning="yes",
                supporting_evidence=[EvidenceReference(evidence_id="ev-1", filename="a", explanation="a")],
                contradicting_evidence=[], missing_evidence=[]
            )
        ]
    )
    return {"summary": res.model_dump_json()}


def mock_multi_agent_success():
    """Mocks the output of the finalized multi-agent graph."""
    state: MultiAgentInvestigationState = {
        "investigation_id": uuid.uuid4(),
        "incident_id": uuid.uuid4(),
        "incident_context": {},
        "evidence_payload": [{"id": "ev-1", "filename": "a"}],
        "timeline": [],
        "observations": [Observation(description="test", evidence_id="ev-1", timeline_event_ids=[])],
        "hypotheses": [
            MultiAgentHypothesis(
                id="H-1", hypothesis="DB overloaded", reasoning="yes",
                supporting_evidence=[EvidenceReference(evidence_id="ev-1", filename="a", explanation="a")],
                contradicting_evidence=[], missing_evidence=[],
                immediate_mitigations=["Restart"], preventative_measures=[]
            )
        ],
        "validation_findings": [],
        "ranking": [RankedHypothesis(hypothesis_id="H-1", rank=1, confidence_rationale="")],
        "recommendations": RecommendationResult(immediate_mitigations=["Restart"], preventative_measures=[]),
        "summary": None,
        "errors": []
    }
    return finalize_result(state)


def test_valid_scenario_comparison():
    # Evaluate Single-Agent
    sa_state = mock_single_agent_success()
    sa_metrics = evaluate_investigation(sa_state, supplied_evidence_ids={"ev-1"}, expected_failure=False)
    
    assert sa_metrics.score == 1.0
    assert sa_metrics.is_grounded == True
    
    # Evaluate Multi-Agent
    ma_state = mock_multi_agent_success()
    ma_metrics = evaluate_investigation(ma_state, supplied_evidence_ids={"ev-1"}, expected_failure=False)
    
    assert ma_metrics.score == 1.0
    assert ma_metrics.is_grounded == True


def test_hallucinated_evidence_scenario():
    # Legacy Single Agent often accepts or generates hallucinated evidence since it has no guardrails natively.
    sa_hallucinated = InvestigationAIResult(
        summary="DB incident", root_cause="DB overloaded", recommendations="Restart",
        supporting_evidence=[EvidenceReference(evidence_id="ev-fake", filename="a", explanation="a")], # Hallucination!
        contradicting_evidence=[], missing_evidence=[], hypotheses=[]
    )
    sa_state = {"summary": sa_hallucinated.model_dump_json()}
    
    # Multi-Agent strictly intercepts it and fails safely (simulating errors populated by validation nodes)
    ma_state = {"errors": ["Validation Error: Hallucinated evidence_id 'ev-fake'"]}
    
    # Evaluate Single-Agent: It fails grounding metric
    sa_metrics = evaluate_investigation(sa_state, supplied_evidence_ids={"ev-1"}, expected_failure=True)
    assert sa_metrics.is_grounded == False
    assert sa_metrics.safe_failure_triggered == False # Single agent didn't realize it failed safely
    
    # Evaluate Multi-Agent: It successfully triggers safe failure
    ma_metrics = evaluate_investigation(ma_state, supplied_evidence_ids={"ev-1"}, expected_failure=True)
    assert ma_metrics.safe_failure_triggered == True
    assert ma_metrics.score == 1.0 # Awarded for failing safely when expected!


def test_malformed_json_scenario():
    # Single-Agent parser crash
    sa_state = {"summary": "Broken JSON } {"}
    sa_metrics = evaluate_investigation(sa_state, supplied_evidence_ids={"ev-1"}, expected_failure=True)
    # The evaluator considers it a schema compliance failure, but since we didn't populate "errors" explicitly it isn't "safely" failing, it's just broken.
    # Wait, our evaluator checks if `summary` fails parsing it returns default metrics (0.0).
    assert sa_metrics.score == 0.0
    assert sa_metrics.is_schema_compliant == False
    
    # Multi-Agent intercepts parsing crashes as explicit deterministic errors in the array
    ma_state = {"errors": ["Failed to generate structured hypotheses: OutputParserException"]}
    ma_metrics = evaluate_investigation(ma_state, supplied_evidence_ids={"ev-1"}, expected_failure=True)
    assert ma_metrics.safe_failure_triggered == True
    assert ma_metrics.score == 1.0
