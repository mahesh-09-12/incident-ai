# apps/api/tests/evaluation/test_validation.py
import pytest
from pydantic import ValidationError
from app.features.investigation.schema import InvestigationAIResult

from tests.evaluation.scenarios import (
    SCENARIO_A_VALID,
    SCENARIO_B_INVALID_EVIDENCE_ID,
    SCENARIO_C_MALFORMED,
    SCENARIO_D_MISSING_INFO,
    SUPPLIED_EVIDENCE_POOL,
)

def validate_evidence_references(result: InvestigationAIResult, supplied_evidence_ids: set[str]):
    """
    Evaluates that all evidence_id references in the structured result
    actually belong to the supplied_evidence_ids set.
    """
    def check_refs(refs):
        for ref in refs:
            assert ref.evidence_id in supplied_evidence_ids, f"Hallucinated evidence_id: {ref.evidence_id}"

    # Check top-level
    check_refs(result.supporting_evidence)
    check_refs(result.contradicting_evidence)

    # Check hypotheses
    for hyp in result.hypotheses:
        check_refs(hyp.supporting_evidence)
        check_refs(hyp.contradicting_evidence)


def test_scenario_a_valid_parsing():
    """
    Verifies that a fully well-formed scenario passes schema validation
    and evidence grounding checks.
    """
    result = InvestigationAIResult.model_validate(SCENARIO_A_VALID)
    assert result.summary == "Database connection pool exhausted."
    assert result.root_cause == "H1"
    assert len(result.hypotheses) == 1
    assert result.hypotheses[0].id == "H1"
    
    # Grounding check
    validate_evidence_references(result, SUPPLIED_EVIDENCE_POOL)


def test_scenario_b_invalid_evidence():
    """
    Verifies that if the LLM hallucinates an evidence ID not in the pool,
    the evaluation logic cleanly catches it.
    """
    result = InvestigationAIResult.model_validate(SCENARIO_B_INVALID_EVIDENCE_ID)
    
    with pytest.raises(AssertionError) as exc_info:
        validate_evidence_references(result, SUPPLIED_EVIDENCE_POOL)
        
    assert "Hallucinated evidence_id: ev-fake-999" in str(exc_info.value)


def test_scenario_c_malformed_output():
    """
    Verifies that missing required fields predictably trigger Pydantic ValidationErrors.
    """
    with pytest.raises(ValidationError) as exc_info:
        InvestigationAIResult.model_validate(SCENARIO_C_MALFORMED)
        
    # 'root_cause' is missing
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("root_cause",) for e in errors)


def test_scenario_d_missing_info_handling():
    """
    Verifies that valid, explicitly missing evidence is parsed correctly
    without forcing false hypotheses.
    """
    result = InvestigationAIResult.model_validate(SCENARIO_D_MISSING_INFO)
    
    assert len(result.missing_evidence) == 2
    assert "Need application logs to confirm." in result.missing_evidence
    assert len(result.supporting_evidence) == 0
    assert len(result.contradicting_evidence) == 0
    
    assert len(result.hypotheses) == 1
    assert "Need application logs to confirm." in result.hypotheses[0].missing_evidence
    
    # Grounding check should pass since there are no invalid file references
    validate_evidence_references(result, SUPPLIED_EVIDENCE_POOL)
