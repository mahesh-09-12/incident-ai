from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    status: str
    summary: str | None
    root_cause: str | None
    recommendations: str | None
    created_at: datetime
    completed_at: datetime | None

class InvestigationAIResult(BaseModel):
    summary: str
    root_cause: str
    recommendations: str