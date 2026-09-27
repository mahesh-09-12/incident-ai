from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.features.investigation.agents.llm_wrapper import get_llm

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    Observation,
)

class EvidenceAnalysisResult(BaseModel):
    observations: list[Observation] = Field(description="List of factual observations derived exclusively from the provided evidence.")

ANALYSIS_PROMPT = """
You are an expert infrastructure and software investigator.
Your task is to analyze the provided evidence and extract objective, factual observations.

Rules:
1. ONLY use the provided evidence text and timeline.
2. NEVER invent or hallucinate facts, timestamps, or evidence IDs.
3. Every observation MUST reference at least one valid evidence_id from the supplied list.
4. If an observation correlates to a specific point in time, reference the valid timeline_event_id.
5. Do NOT form conclusions or hypotheses yet, only factual observations.

Evidence Provided:
{evidence}

Timeline Events:
{timeline}
"""

def _format_evidence(evidence_payload: list[dict]) -> str:
    if not evidence_payload:
        return "No evidence provided."
    
    formatted_items = []
    for item in evidence_payload:
        content = item.get('content', '')
        formatted_items.append(f"--- Evidence ID: {item.get('id')} | Filename: {item.get('filename')} ---\n{content}")
        
    return "\n\n".join(formatted_items)

def _format_timeline(timeline: list) -> str:
    if not timeline:
        return "No timeline events provided."
    return "\n".join(
        f"[{item.line_number}] {item.timestamp} (Source: {item.evidence_id}): {item.content}"
        for item in timeline
    )

def analyze_evidence_node(state: MultiAgentInvestigationState) -> dict:
    evidence_payload = state.get("evidence_payload", [])
    if not evidence_payload:
        return {"errors": ["No evidence provided for analysis."]}

    valid_evidence_ids = {str(e.get("id")) for e in evidence_payload if "id" in e}
    valid_timeline_ids = {t.line_number for t in state.get("timeline", [])}

    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(EvidenceAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYSIS_PROMPT),
        ("human", "Analyze the evidence and extract observations.")
    ])

    chain = prompt | structured_llm

    try:
        # Pass the formatted strings to the chain
        result: EvidenceAnalysisResult = chain.invoke({
            "evidence": _format_evidence(evidence_payload),
            "timeline": _format_timeline(state.get("timeline", []))
        })
    except Exception as e:
        return {"errors": [f"Failed to generate structured observations: {str(e)}"]}

    # Deterministic Validation
    valid_observations = []
    errors = []
    
    for obs in result.observations:
        if obs.evidence_id not in valid_evidence_ids:
            errors.append(f"Validation Error: Hallucinated evidence_id '{obs.evidence_id}'.")
            continue
            
        invalid_tl_ids = [t_id for t_id in obs.timeline_event_ids if t_id not in valid_timeline_ids]
        if invalid_tl_ids:
            errors.append(f"Validation Error: Hallucinated timeline_event_ids {invalid_tl_ids}.")
            continue
            
        valid_observations.append(obs)

    output = {}
    if valid_observations:
        output["observations"] = valid_observations
    if errors:
        output["errors"] = errors
        
    return output
