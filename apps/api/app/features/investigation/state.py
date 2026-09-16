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

    error: str | None