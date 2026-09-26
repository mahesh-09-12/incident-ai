from pydantic import BaseModel
from typing import Any
import json

from app.features.investigation.schema import InvestigationAIResult


class EvaluationMetrics(BaseModel):
    is_schema_compliant: bool
    is_grounded: bool
    has_valid_hypotheses: bool
    is_traceable: bool
    safe_failure_triggered: bool
    score: float


def evaluate_investigation(
    final_state: dict[str, Any],
    supplied_evidence_ids: set[str],
    expected_failure: bool = False
) -> EvaluationMetrics:
    """
    Deterministically evaluates an investigation result graph state against objective metrics.
    """
    metrics = EvaluationMetrics(
        is_schema_compliant=False,
        is_grounded=False,
        has_valid_hypotheses=False,
        is_traceable=False,
        safe_failure_triggered=False,
        score=0.0
    )

    # 1. Check Safe Failure Handling
    errors = final_state.get("errors", [])
    has_terminal_error = len(errors) > 0 or "summary" not in final_state
    
    if has_terminal_error:
        if expected_failure:
            metrics.safe_failure_triggered = True
            metrics.score = 1.0 # Perfect score for failing safely when expected
        return metrics

    if expected_failure and not has_terminal_error:
        # Failed to fail safely
        return metrics

    # 2. Schema Adherence
    summary_str = final_state.get("summary")
    try:
        if isinstance(summary_str, str):
            result_dict = json.loads(summary_str)
            result = InvestigationAIResult(**result_dict)
        else:
            # Maybe it's a model instance already (legacy graph might do this directly)
            result = InvestigationAIResult.model_validate(summary_str)
            
        metrics.is_schema_compliant = True
    except Exception:
        # Fails schema compliance
        return metrics

    # 3. Evidence Grounding
    all_refs = (
        result.supporting_evidence + 
        result.contradicting_evidence
    )
    
    # Check all hypotheses evidence
    for hyp in result.hypotheses:
        all_refs.extend(hyp.supporting_evidence)
        all_refs.extend(hyp.contradicting_evidence)

    metrics.is_grounded = True
    for ref in all_refs:
        if ref.evidence_id not in supplied_evidence_ids:
            metrics.is_grounded = False
            break

    # 4. Hypothesis Quality
    if len(result.hypotheses) > 0:
        metrics.has_valid_hypotheses = True
        for hyp in result.hypotheses:
            if not hyp.hypothesis or not hyp.id:
                metrics.has_valid_hypotheses = False
                break
                
    # 5. Traceability
    # The root cause string should loosely match the top hypothesis if traceable
    metrics.is_traceable = False
    if metrics.has_valid_hypotheses:
        for hyp in result.hypotheses:
            if hyp.hypothesis in result.root_cause or result.root_cause in hyp.hypothesis:
                metrics.is_traceable = True
                break
                
    # Score Calculation
    score_components = [
        metrics.is_schema_compliant,
        metrics.is_grounded,
        metrics.has_valid_hypotheses,
        metrics.is_traceable
    ]
    
    metrics.score = sum(1 for c in score_components if c) / len(score_components)
    
    return metrics
