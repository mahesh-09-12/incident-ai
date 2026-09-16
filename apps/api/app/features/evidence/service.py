from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.features.evidence.repository import EvidenceRepository
from app.features.incident.repository import IncidentRepository


STORAGE_DIR = Path("storage/evidence")

ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "text/csv",
    "application/json",
    "application/yaml",
    "text/yaml",
    "application/octet-stream",
}


class EvidenceService:
    def __init__(self, db: Session):
        self.evidence_repository = EvidenceRepository(db)
        self.incident_repository = IncidentRepository(db)

    async def upload_evidence(
        self,
        incident_id: UUID,
        file: UploadFile,
    ):
        incident = self.incident_repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type",
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File cannot be empty",
            )

        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4()}_{file.filename}"
        storage_path = STORAGE_DIR / stored_filename

        storage_path.write_bytes(file_content)

        evidence = self.evidence_repository.create(
            incident_id=incident_id,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(file_content),
            storage_path=str(storage_path),
        )

        return evidence
    
    def list_evidence(self, incident_id: UUID):
        incident = self.incident_repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return self.evidence_repository.list_by_incident(incident_id)
    
    def get_evidence(self, evidence_id: UUID):
        evidence = self.evidence_repository.get_by_id(evidence_id)

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )

        return evidence
    
    def delete_evidence(self, evidence_id: UUID):
        evidence = self.evidence_repository.get_by_id(evidence_id)

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )

        storage_path = Path(evidence.storage_path)

        if storage_path.exists():
            storage_path.unlink()

        self.evidence_repository.delete(evidence)