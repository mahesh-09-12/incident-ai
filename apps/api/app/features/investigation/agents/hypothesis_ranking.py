from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    RankedHypothesis,
    MultiAgentHypothesis,
    ValidationFinding,
)

def rank_hypotheses_node(state: MultiAgentInvestigationState) -> dict:
    """
    Deterministically ranks hypotheses based on validation findings.
    Does not use an LLM.
    """
    hypotheses: list[MultiAgentHypothesis] = state.get("hypotheses", [])
    validation_findings: list[ValidationFinding] = state.get("validation_findings", [])

    if not hypotheses:
        return {"ranking": []}
        
    if not validation_findings:
        return {"errors": ["Cannot rank hypotheses: No validation findings provided."]}

    # Build a lookup for findings
    finding_map = {}
    for finding in validation_findings:
        # If multiple findings exist for the same hypothesis, we safely overwrite 
        # (or reject duplicate in testing). For deterministic behavior, keep the first one.
        if finding.hypothesis_id not in finding_map:
            finding_map[finding.hypothesis_id] = finding

    scored_hypotheses = []
    errors = []
    seen_ids = set()

    for hyp in hypotheses:
        if hyp.id in seen_ids:
            errors.append(f"Ranking Error: Duplicate hypothesis ID '{hyp.id}' detected.")
            continue
            
        seen_ids.add(hyp.id)
        
        finding = finding_map.get(hyp.id)
        if not finding:
            errors.append(f"Ranking Error: No validation finding for hypothesis '{hyp.id}'.")
            continue

        # Scoring Logic
        score = 0
        rationale_parts = []
        
        if finding.is_valid:
            score += 100
            rationale_parts.append("Validated (+100)")
        else:
            rationale_parts.append("Not validated (+0)")
            
        num_supporting = len(hyp.supporting_evidence)
        if num_supporting > 0:
            score += num_supporting * 10
            rationale_parts.append(f"{num_supporting} supporting evidence (+{num_supporting * 10})")
            
        num_contradicting_hyp = len(hyp.contradicting_evidence)
        if num_contradicting_hyp > 0:
            score -= num_contradicting_hyp * 20
            rationale_parts.append(f"{num_contradicting_hyp} intrinsic contradictions (-{num_contradicting_hyp * 20})")
            
        num_contradicting_val = len(finding.contradicting_evidence)
        if num_contradicting_val > 0:
            score -= num_contradicting_val * 20
            rationale_parts.append(f"{num_contradicting_val} validation contradictions (-{num_contradicting_val * 20})")
            
        num_missing = len(hyp.missing_evidence)
        if num_missing > 0:
            score -= num_missing * 5
            rationale_parts.append(f"{num_missing} missing evidence (-{num_missing * 5})")

        confidence_rationale = f"Score: {score}. " + ", ".join(rationale_parts) + "."

        scored_hypotheses.append({
            "id": hyp.id,
            "score": score,
            "rationale": confidence_rationale
        })

    # Sort deterministically: highest score first, ties broken by ID (alphabetically ascending)
    # Since we want highest score, we sort by (-score, id)
    scored_hypotheses.sort(key=lambda x: (-x["score"], x["id"]))

    ranked_results = []
    for rank_idx, sh in enumerate(scored_hypotheses):
        ranked_results.append(RankedHypothesis(
            hypothesis_id=sh["id"],
            rank=rank_idx + 1,
            confidence_rationale=sh["rationale"]
        ))

    output = {}
    if ranked_results:
        output["ranking"] = ranked_results
    if errors:
        output["errors"] = errors
        
    return output
