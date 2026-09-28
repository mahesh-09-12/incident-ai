from dataclasses import dataclass
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from sqlalchemy.orm import Session

from app.features.incident.repository import IncidentRepository
from app.features.investigation.state import InvestigationState
from app.features.investigation.schema import InvestigationAIResult
from app.features.investigation.repository import InvestigationRepository

from app.features.evidence.repository import EvidenceRepository
from app.features.evidence.storage import get_evidence_content_bytes

from app.features.investigation.agents.llm_wrapper import get_llm

@dataclass
class InvestigationContext:
    db: Session
    owner_id: str


def load_incident(
    state: InvestigationState,
    runtime: Runtime[InvestigationContext],
) -> InvestigationState:
    repository = IncidentRepository(runtime.context.db, runtime.context.owner_id)

    incident = repository.get_by_id(state["incident_id"])

    if not incident:
        raise ValueError("Incident not found")

    state["incident"] = {
        "id": str(incident.id),
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "environment": incident.environment,
        "service": incident.service,
        "status": incident.status,
    }

    return state


def load_evidence(
    state: InvestigationState,
    runtime: Runtime[InvestigationContext],
) -> InvestigationState:
    repository = EvidenceRepository(runtime.context.db)

    evidence_items = repository.list_by_incident(
        state["incident_id"]
    )

    evidence = []

    for item in evidence_items:
        content = get_evidence_content_bytes(item).decode("utf-8", errors="replace")

        evidence.append(
            {
                "id": str(item.id),
                "filename": item.filename,
                "content_type": item.content_type,
                "file_size": item.file_size,
                "storage_path": item.storage_path,
                "content": content,
            }
        )

    state["evidence"] = evidence

    return state


def analyze_evidence(state: InvestigationState) -> InvestigationState:
    llm = get_llm(temperature=0)

    structured_llm = llm.with_structured_output(
        InvestigationAIResult
    )

    evidence_text = "\n\n".join(
        f"--- Evidence ID: {item['id']} | Filename: {item['filename']} ---\n{item['content']}" 
        for item in state["evidence"]
    )

    prompt = f"""
You are an incident investigation assistant.

Analyze this production incident using ONLY the provided incident
information and evidence.

Incident:
Title: {state["incident"]["title"]}
Description: {state["incident"]["description"]}
Severity: {state["incident"]["severity"]}
Environment: {state["incident"]["environment"]}
Service: {state["incident"]["service"]}

Evidence:
{evidence_text}

Provide:

- summary: A concise summary of what happened.
- hypotheses: A list of 2 to 4 plausible technical hypotheses. Each hypothesis must have:
  - id: A unique string identifier (e.g., "H1").
  - hypothesis: The text of the technical hypothesis.
  - reasoning: A brief explanation of why this hypothesis is considered.
  - supporting_evidence: A list of evidence objects actually present that support this hypothesis. Each object MUST contain `evidence_id`, `filename`, and `explanation`.
  - contradicting_evidence: A list of evidence objects actually present that contradict this hypothesis. Return an empty list if none. Each object MUST contain `evidence_id`, `filename`, and `explanation`.
  - missing_evidence: A list of strings detailing missing information that would be useful for testing this hypothesis but is NOT currently available. Return an empty list if none.
- root_cause: The most likely technical root cause among your hypotheses. Clearly state uncertainty if the evidence is insufficient. This should identify the currently most supported hypothesis, not pretend certainty.
- supporting_evidence: Aggregate list of the most critical supporting evidence objects.
- contradicting_evidence: Aggregate list of the most critical contradicting evidence objects.
- missing_evidence: Aggregate list of missing information across all hypotheses.
- recommendations: Practical actions to investigate, mitigate, and prevent recurrence.

Do not invent facts, logs, metrics, timestamps, deployments, traces, or evidence IDs that are not present in the provided information.
If there is no supporting or contradicting evidence, return an empty list for those fields.
"""

    result = structured_llm.invoke(prompt)

    state["summary"] = result.summary
    state["root_cause"] = result.root_cause
    state["recommendations"] = result.recommendations
    state["supporting_evidence"] = [e.model_dump() for e in result.supporting_evidence]
    state["contradicting_evidence"] = [e.model_dump() for e in result.contradicting_evidence]
    state["missing_evidence"] = result.missing_evidence
    state["hypotheses"] = [h.model_dump() for h in result.hypotheses]

    return state


def save_result(
    state: InvestigationState,
    runtime: Runtime[InvestigationContext],
) -> InvestigationState:
    repository = InvestigationRepository(runtime.context.db)

    investigation = repository.get_by_id(
        state["investigation_id"]
    )

    if not investigation:
        raise ValueError("Investigation not found")

    repository.complete(
        investigation,
        summary=state["summary"] or "",
        root_cause=state["root_cause"] or "",
        recommendations=state["recommendations"] or "",
        supporting_evidence=state["supporting_evidence"],
        contradicting_evidence=state["contradicting_evidence"],
        missing_evidence=state["missing_evidence"],
        hypotheses=state["hypotheses"],
    )

    return state


def build_investigation_graph():
    graph = StateGraph(
        InvestigationState,
        context_schema=InvestigationContext,
    )

    graph.add_node("load_incident", load_incident)
    graph.add_node("load_evidence", load_evidence)
    graph.add_node("analyze_evidence", analyze_evidence)
    graph.add_node("save_result", save_result)

    graph.add_edge(START, "load_incident")
    graph.add_edge("load_incident", "load_evidence")
    graph.add_edge("load_evidence", "analyze_evidence")
    graph.add_edge("analyze_evidence", "save_result")
    graph.add_edge("save_result", END)

    return graph.compile()