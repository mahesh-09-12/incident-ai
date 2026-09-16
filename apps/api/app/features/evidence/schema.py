from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    created_at: datetime