from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    severity: str
    environment: str
    service: str = Field(min_length=1, max_length=100)


class IncidentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
    )
    severity: str | None = None
    environment: str | None = None
    service: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    status: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    severity: str
    environment: str
    service: str
    status: str
    created_at: datetime