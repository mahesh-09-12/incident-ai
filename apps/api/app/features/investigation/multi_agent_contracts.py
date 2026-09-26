from typing import TypedDict, Annotated
import operator
from pydantic import BaseModel
from uuid import UUID

from app.features.investigation.schema import EvidenceReference
from app.features.investigation.timeline import TimelineEvent


class Observation(BaseModel):
    description: str
    evidence_id: str
    timeline_event_ids: list[int]


class MultiAgentHypothesis(BaseModel):
    """
    Enhanced Hypothesis model specific for multi-agent validation.
    """
    id: str
    hypothesis: str
    reasoning: str
    supporting_evidence: list[EvidenceReference]
    contradicting_evidence: list[EvidenceReference]
    missing_evidence: list[str]
    immediate_mitigations: list[str]
    preventative_measures: list[str]


class ValidationFinding(BaseModel):
    hypothesis_id: str
    is_valid: bool
    contradicting_evidence: list[EvidenceReference]
    uncertainty_rationale: str


class RankedHypothesis(BaseModel):
    hypothesis_id: str
    rank: int
    confidence_rationale: str


class RecommendationResult(BaseModel):
    immediate_mitigations: list[str]
    preventative_measures: list[str]


class MultiAgentInvestigationState(TypedDict):
    investigation_id: UUID
    incident_id: UUID
    
    # Deterministic Data
    incident_context: dict | None
    evidence_payload: list[dict]
    timeline: list[TimelineEvent]
    
    # Agent Outputs
    observations: list[Observation]
    hypotheses: list[MultiAgentHypothesis]
    validation_findings: list[ValidationFinding]
    ranking: list[RankedHypothesis]
    recommendations: RecommendationResult | None
    summary: str | None
    
    # Error Handling - Using operator.add for safe list concatenation via LangGraph
    errors: Annotated[list[str], operator.add]
    warnings: Annotated[list[str], operator.add]
