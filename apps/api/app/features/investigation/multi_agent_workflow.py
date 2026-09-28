from dataclasses import dataclass
from pathlib import Path
import logging
import time
from functools import wraps

from sqlalchemy.orm import Session
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

def with_observability(node_name: str):
    """
    Wraps a LangGraph node to provide structured logging for execution time and errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[MultiAgent] START {node_name}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"[MultiAgent] END {node_name} elapsed={elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[MultiAgent] ERROR {node_name} elapsed={elapsed:.2f}s error={str(e)}")
                raise
        return wrapper
    return decorator

from app.features.incident.repository import IncidentRepository
from app.features.evidence.repository import EvidenceRepository
from app.features.evidence.storage import get_evidence_content_bytes
from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    MultiAgentHypothesis,
)
from app.features.investigation.schema import InvestigationAIResult, Hypothesis
from app.features.investigation.timeline import extract_timeline

from app.features.investigation.agents.evidence_analysis import analyze_evidence_node
from app.features.investigation.agents.investigate_hypotheses import investigate_hypotheses_node
from app.features.investigation.agents.hypothesis_ranking import rank_hypotheses_node
from app.features.investigation.agents.recommendation import generate_recommendations_node

@dataclass
class MultiAgentContext:
    db: Session

def load_incident_data(
    state: MultiAgentInvestigationState,
    runtime: Runtime[MultiAgentContext],
) -> dict:
    """
    Deterministically loads incident context and evidence payload into the graph state.
    """
    if state.get("incident_context") and state.get("evidence_payload"):
        return {}

    incident_repo = IncidentRepository(runtime.context.db)
    evidence_repo = EvidenceRepository(runtime.context.db)

    incident = incident_repo.get_by_id(state["incident_id"])
    if not incident:
        raise ValueError(f"Incident {state['incident_id']} not found")

    incident_context = {
        "id": str(incident.id),
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "environment": incident.environment,
        "service": incident.service,
        "status": incident.status,
    }

    evidence_items = evidence_repo.list_by_incident(state["incident_id"])
    evidence_payload = []

    for item in evidence_items:
        content = get_evidence_content_bytes(item).decode("utf-8", errors="replace")
        evidence_payload.append({
            "id": str(item.id),
            "filename": item.filename,
            "content_type": item.content_type,
            "file_size": item.file_size,
            "storage_path": item.storage_path,
            "content": content,
        })

    return {
        "incident_context": incident_context,
        "evidence_payload": evidence_payload,
        "errors": []
    }

def build_timeline_node(state: MultiAgentInvestigationState) -> dict:
    """
    Extracts the deterministic timeline from the loaded evidence payload.
    """
    evidence_payload = state.get("evidence_payload", [])
    if not evidence_payload:
        return {"errors": ["Cannot build timeline: No evidence provided."]}
        
    evidence_tuples = [
        (e.get("id"), e.get("filename"), e.get("content"))
        for e in evidence_payload
    ]
        
    timeline_events = extract_timeline(evidence_tuples)
    return {"timeline": timeline_events}


def finalize_result(state: MultiAgentInvestigationState) -> dict:
    """
    Converts the internal multi-agent state into the standard InvestigationAIResult format.
    Ensures safe error bubbling and deterministic mappings.
    """
    errors = state.get("errors", [])
    if errors:
        raise ValueError(f"Graph execution failed with errors: {'; '.join(errors)}")
        
    # If any required state is missing, fail safely
    ranking = state.get("ranking", [])
    hypotheses: list[MultiAgentHypothesis] = state.get("hypotheses", [])
    recommendations = state.get("recommendations")
    observations = state.get("observations", [])
    
    if not recommendations:
        raise ValueError("Cannot finalize result: Missing essential investigation outputs.")
        
    if not hypotheses:
        # No hypotheses generated
        summary_text = f"Multi-Agent investigation concluded. Extracted {len(observations)} critical observations. No hypotheses were successfully validated."
        
        result = InvestigationAIResult(
            summary=summary_text,
            root_cause="No root cause identified. The evidence did not support any technical hypotheses.",
            recommendations="Immediate Mitigations:\n- None\n\nPreventative Measures:\n- None",
            supporting_evidence=[],
            contradicting_evidence=[],
            missing_evidence=[],
            hypotheses=[]
        )
        return {"summary": result.model_dump_json()}
        
    if not ranking:
        raise ValueError("Cannot finalize result: Missing essential investigation outputs (ranking).")
        
    hyp_map = {h.id: h for h in hypotheses}
    
    # Identify the highest ranked hypothesis
    top_rank = ranking[0]
    top_hypothesis = hyp_map.get(top_rank.hypothesis_id)
    if not top_hypothesis:
        raise ValueError("Cannot finalize result: Top ranked hypothesis not found in hypotheses list.")
        
    # Convert internal MultiAgentHypothesis to public Hypothesis schema
    public_hypotheses = []
    for internal_hyp in hypotheses:
        public_hypotheses.append(
            Hypothesis(
                id=internal_hyp.id,
                hypothesis=internal_hyp.hypothesis,
                reasoning=internal_hyp.reasoning,
                supporting_evidence=internal_hyp.supporting_evidence,
                contradicting_evidence=internal_hyp.contradicting_evidence,
                missing_evidence=internal_hyp.missing_evidence
            )
        )
        
    summary_text = (
        f"Multi-Agent investigation concluded. Extracted {len(observations)} critical observations. "
        f"Generated and validated {len(hypotheses)} hypotheses."
    )
    
    recs_text = "Immediate Mitigations:\n" + "\n".join(f"- {r}" for r in recommendations.immediate_mitigations) + "\n\n"
    recs_text += "Preventative Measures:\n" + "\n".join(f"- {r}" for r in recommendations.preventative_measures)

    # Return state mapped cleanly back to the old string summary representation but with structural arrays intact
    result = InvestigationAIResult(
        summary=summary_text,
        root_cause=top_hypothesis.hypothesis, # Provide the top hypothesis text as the "root cause"
        recommendations=recs_text,
        supporting_evidence=top_hypothesis.supporting_evidence,
        contradicting_evidence=top_hypothesis.contradicting_evidence,
        missing_evidence=top_hypothesis.missing_evidence,
        hypotheses=public_hypotheses
    )
    
    return {"summary": result.model_dump_json()}


# Assemble Graph
workflow = StateGraph(MultiAgentInvestigationState)

workflow.add_node("load_incident_data", with_observability("load_incident_data")(load_incident_data))
workflow.add_node("build_timeline", with_observability("build_timeline")(build_timeline_node))
workflow.add_node("analyze_evidence", with_observability("analyze_evidence")(analyze_evidence_node))
workflow.add_node("investigate_hypotheses", with_observability("investigate_hypotheses")(investigate_hypotheses_node))
workflow.add_node("rank_hypotheses", with_observability("rank_hypotheses")(rank_hypotheses_node))
workflow.add_node("generate_recommendations", with_observability("generate_recommendations")(generate_recommendations_node))
workflow.add_node("finalize_result", with_observability("finalize_result")(finalize_result))

workflow.add_edge(START, "load_incident_data")
workflow.add_edge("load_incident_data", "build_timeline")
workflow.add_edge("build_timeline", "analyze_evidence")
workflow.add_edge("analyze_evidence", "investigate_hypotheses")
workflow.add_edge("investigate_hypotheses", "rank_hypotheses")
workflow.add_edge("rank_hypotheses", "generate_recommendations")
workflow.add_edge("generate_recommendations", "finalize_result")
workflow.add_edge("finalize_result", END)

multi_agent_graph = workflow.compile()
