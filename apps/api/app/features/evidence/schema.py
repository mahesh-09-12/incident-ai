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
    storage_path: str | None = None
    cloudinary_public_id: str | None = None
    cloudinary_asset_id: str | None = None
    cloudinary_resource_type: str | None = None
    cloudinary_delivery_type: str | None = None
    created_at: datetime