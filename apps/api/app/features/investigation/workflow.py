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

from langchain_ollama import ChatOllama

@dataclass
class InvestigationContext:
    db: Session


def load_incident(
    state: InvestigationState,
    runtime: Runtime[InvestigationContext],
) -> InvestigationState:
    repository = IncidentRepository(runtime.context.db)

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
        path = Path(item.storage_path)

        if not path.exists():
            raise ValueError(
                f"Evidence file not found: {item.filename}"
            )

        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

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
    llm = ChatOllama(
        model="qwen3:4b",
        temperature=0,
    )

    structured_llm = llm.with_structured_output(
        InvestigationAIResult
    )

    evidence_text = "\n\n".join(
        f"--- {item['filename']} ---\n{item['content']}" 
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
- root_cause: The most likely technical root cause, including the
  evidence supporting it. Clearly state uncertainty if the evidence
  is insufficient.
- recommendations: Practical actions to investigate, mitigate, and
  prevent recurrence.

Do not invent facts that are not present in the provided information.
"""

    result = structured_llm.invoke(prompt)

    state["summary"] = result.summary
    state["root_cause"] = result.root_cause
    state["recommendations"] = result.recommendations
    state["analysis"] = (
        f"Summary: {result.summary}\n\n"
        f"Root Cause: {result.root_cause}\n\n"
        f"Recommendations: {result.recommendations}"
    )

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