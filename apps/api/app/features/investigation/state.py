from typing import TypedDict
from uuid import UUID


class InvestigationState(TypedDict):
    investigation_id: UUID
    incident_id: UUID

    incident: dict | None
    evidence: list[dict]

    analysis: str | None
    summary: str | None
    root_cause: str | None
    recommendations: str | None
    supporting_evidence: list[dict] | None
    contradicting_evidence: list[dict] | None
    missing_evidence: list[str] | None
    hypotheses: list[dict] | None

    error: str | None