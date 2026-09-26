from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EvidenceReference(BaseModel):
    evidence_id: str
    filename: str
    explanation: str


class Hypothesis(BaseModel):
    id: str
    hypothesis: str
    supporting_evidence: list[EvidenceReference]
    contradicting_evidence: list[EvidenceReference]
    missing_evidence: list[str]
    reasoning: str


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    status: str
    summary: str | None
    root_cause: str | None
    recommendations: str | None
    supporting_evidence: list[EvidenceReference] | None = None
    contradicting_evidence: list[EvidenceReference] | None = None
    missing_evidence: list[str] | None = None
    hypotheses: list[Hypothesis] | None = None
    created_at: datetime
    completed_at: datetime | None

class InvestigationAIResult(BaseModel):
    summary: str
    root_cause: str
    recommendations: str
    supporting_evidence: list[EvidenceReference]
    contradicting_evidence: list[EvidenceReference]
    missing_evidence: list[str]
    hypotheses: list[Hypothesis]