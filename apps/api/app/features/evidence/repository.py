from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.evidence.model import Evidence


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        incident_id: UUID,
        filename: str,
        content_type: str,
        file_size: int,
        storage_path: str | None = None,
        cloudinary_public_id: str | None = None,
        cloudinary_asset_id: str | None = None,
        cloudinary_resource_type: str | None = None,
        cloudinary_delivery_type: str | None = None,
    ) -> Evidence:
        evidence = Evidence(
            incident_id=incident_id,
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            storage_path=storage_path,
            cloudinary_public_id=cloudinary_public_id,
            cloudinary_asset_id=cloudinary_asset_id,
            cloudinary_resource_type=cloudinary_resource_type,
            cloudinary_delivery_type=cloudinary_delivery_type,
        )

        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)

        return evidence

    def get_by_id(self, evidence_id: UUID) -> Evidence | None:
        statement = select(Evidence).where(Evidence.id == evidence_id)

        return self.db.scalar(statement)

    def list_by_incident(
        self,
        incident_id: UUID,
    ) -> list[Evidence]:
        statement = (
            select(Evidence)
            .where(Evidence.incident_id == incident_id)
            .order_by(Evidence.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def delete(self, evidence: Evidence) -> None:
        self.db.delete(evidence)
        self.db.commit()