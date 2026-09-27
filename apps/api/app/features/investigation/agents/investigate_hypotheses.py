import uuid
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.features.investigation.agents.llm_wrapper import get_llm

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    MultiAgentHypothesis,
    ValidationFinding,
)
from app.features.investigation.schema import EvidenceReference

class InvestigatedHypothesis(BaseModel):
    id: str
    hypothesis: str
    reasoning: str
    supporting_evidence: list[str] = Field(description="List of EXACT evidence IDs (e.g., 'ev-1') that support this hypothesis. Do NOT include log messages, timestamps, or explanations.")
    contradicting_evidence: list[str] = Field(description="List of EXACT evidence IDs (e.g., 'ev-1') that contradict this hypothesis. Do NOT include log messages, timestamps, or explanations.")
    missing_evidence: list[str]
    immediate_mitigations: list[str] = Field(description="Immediate steps to mitigate or restore service if this hypothesis is true.")
    preventative_measures: list[str] = Field(description="Long-term preventative measures to avoid recurrence if this hypothesis is true.")
    is_valid: bool = Field(description="True ONLY if fully supported by concrete evidence. False if contradicted OR if crucial inferred causes (like deployment configs) are missing evidence.")

class InvestigateHypothesesResult(BaseModel):
    hypotheses: list[InvestigatedHypothesis] = Field(description="List of 1-2 investigated technical hypotheses.")

INVESTIGATION_PROMPT = """
You are an expert infrastructure and software investigator.
Your task is to generate 1 to 2 plausible technical hypotheses explaining the incident, and immediately evaluate them against the supplied observations.

Rules:
1. ONLY base your hypotheses on the provided observations and incident context.
2. NEVER invent facts, metrics, timeline events, or evidence IDs.
3. Every evidence_id referenced MUST physically exist in the supplied list.
4. The supporting_evidence and contradicting_evidence fields MUST contain ONLY exact evidence IDs (e.g., 'ev-1'). Do NOT include log messages, timestamps, filenames, or explanations in these fields.
5. Do NOT claim absolute certainty or identify a definitive root cause yet.
6. If there is insufficient information to form a hypothesis, return an empty list rather than guessing.
7. Provide clear, objective reasoning for each hypothesis.
8. Assign a unique, stable ID to each hypothesis (e.g., 'H1', 'H2').
9. Determine if each hypothesis is fully supported, partially supported, or contradicted by evidence (is_valid).
10. If contradicted, explicitly reference the contradicting evidence using existing evidence_ids.
11. If data is insufficient to validate a hypothesis, clearly state this in the reasoning.
12. Propose immediate_mitigations and preventative_measures for each hypothesis generated.
13. IMPORTANT: Distinguish clearly between observed facts (e.g., 'DB timeout seen in logs') and inferred causes (e.g., 'connection pool exhausted due to bad deployment').
14. If your hypothesis relies on an inferred cause (like a deployment or configuration change) that is NOT explicitly proven by the supplied evidence, you MUST record it in missing_evidence and set is_valid=False. Do NOT treat unverified deployment/configuration inferences as established facts.

Incident Context:
{incident_context}

Observations:
{observations}
"""

def _format_incident_context(context: dict | None) -> str:
    if not context:
        return "No incident context provided."
    return f"Title: {context.get('title')}\nDescription: {context.get('description')}\nService: {context.get('service')}\nEnvironment: {context.get('environment')}"

def _format_observations(observations: list) -> str:
    if not observations:
        return "No observations available."
    return "\n".join(
        f"- [Evidence ID: {obs.evidence_id}] {obs.description}"
        for obs in observations
    )



def investigate_hypotheses_node(state: MultiAgentInvestigationState) -> dict:
    observations = state.get("observations", [])
    if not observations:
        return {"errors": ["Cannot generate hypotheses: No observations provided."]}

    evidence_payload = state.get("evidence_payload", [])
    evidence_id_to_filename = {str(e.get("id")): e.get("filename", "unknown") for e in evidence_payload if "id" in e}
    valid_evidence_ids = set(evidence_id_to_filename.keys())

    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(InvestigateHypothesesResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", INVESTIGATION_PROMPT),
        ("human", "Analyze the context and observations to formulate and validate technical hypotheses.")
    ])

    chain = prompt | structured_llm

    try:
        result: InvestigateHypothesesResult = chain.invoke({
            "incident_context": _format_incident_context(state.get("incident_context")),
            "observations": _format_observations(observations)
        })
    except Exception as e:
        return {"errors": [f"Failed to generate structured hypotheses and validation: {str(e)}"]}

    # Deterministic Validation
    valid_hypotheses = []
    valid_findings = []
    errors = []
    warnings = []
    used_ids = set()

    for item in result.hypotheses:
        # Fallback if LLM failed to generate a stable ID
        hyp_id = item.id if item.id and item.id not in used_ids else f"H-{uuid.uuid4().hex[:6]}"
        used_ids.add(hyp_id)

        valid_supporting = []
        for ref_id in item.supporting_evidence:
            if ref_id in valid_evidence_ids:
                valid_supporting.append(ref_id)
            else:
                warnings.append(f"Validation Warning: Hypothesis '{hyp_id}' hallucinated evidence_id '{ref_id}'.")
                
        valid_contradicting = []
        for ref_id in item.contradicting_evidence:
            if ref_id in valid_evidence_ids:
                valid_contradicting.append(ref_id)
            else:
                warnings.append(f"Validation Warning: Hypothesis '{hyp_id}' hallucinated evidence_id '{ref_id}'.")

        # Deterministically reconstruct EvidenceReference objects
        supporting_refs = [
            EvidenceReference(evidence_id=e_id, filename=evidence_id_to_filename[e_id], explanation=item.reasoning)
            for e_id in valid_supporting
        ]
        contradicting_refs = [
            EvidenceReference(evidence_id=e_id, filename=evidence_id_to_filename[e_id], explanation=item.reasoning)
            for e_id in valid_contradicting
        ]

        valid_hypotheses.append(
            MultiAgentHypothesis(
                id=hyp_id,
                hypothesis=item.hypothesis,
                reasoning=item.reasoning,
                supporting_evidence=supporting_refs,
                contradicting_evidence=contradicting_refs,
                missing_evidence=item.missing_evidence,
                immediate_mitigations=item.immediate_mitigations,
                preventative_measures=item.preventative_measures,
            )
        )
        
        uncertainty_rationale = item.reasoning
        if item.missing_evidence and item.is_valid:
            uncertainty_rationale += " (Deterministically downgraded due to missing evidence)"

        valid_findings.append(
            ValidationFinding(
                hypothesis_id=hyp_id,
                is_valid=False if item.missing_evidence else item.is_valid,
                contradicting_evidence=contradicting_refs,
                uncertainty_rationale=uncertainty_rationale,
            )
        )

    output = {}
    if valid_hypotheses:
        output["hypotheses"] = valid_hypotheses
    if valid_findings:
        output["validation_findings"] = valid_findings
    if errors:
        output["errors"] = errors
    if warnings:
        output["warnings"] = warnings
        
    return output
