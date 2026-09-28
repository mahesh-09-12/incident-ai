from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status, Response
from sqlalchemy.orm import Session
import cloudinary.uploader
import cloudinary.api

from app.core.config import settings
from app.features.evidence.repository import EvidenceRepository
from app.features.incident.repository import IncidentRepository
from app.features.evidence.storage import get_evidence_content_bytes


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
    def __init__(self, db: Session, owner_id: str):
        self.evidence_repository = EvidenceRepository(db)
        self.incident_repository = IncidentRepository(db, owner_id)

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

        if settings.is_cloudinary_enabled:
            # Upload to Cloudinary
            public_id = f"incident_ai/incidents/{incident_id}/evidence/{uuid4()}"
            
            try:
                cloudinary_res = cloudinary.uploader.upload(
                    file_content,
                    public_id=public_id,
                    resource_type="raw",
                    type="authenticated",
                    overwrite=True
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload evidence to Cloudinary: {e}"
                )
                
            evidence = self.evidence_repository.create(
                incident_id=incident_id,
                filename=file.filename,
                content_type=file.content_type or "application/octet-stream",
                file_size=len(file_content),
                storage_path=None,
                cloudinary_public_id=cloudinary_res.get("public_id"),
                cloudinary_asset_id=cloudinary_res.get("asset_id"),
                cloudinary_resource_type=cloudinary_res.get("resource_type"),
                cloudinary_delivery_type=cloudinary_res.get("type"),
            )
        else:
            # Local Storage
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
            
        incident = self.incident_repository.get_by_id(evidence.incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )

        return evidence
    
    def get_evidence_content_response(self, incident_id: UUID, evidence_id: UUID) -> Response:
        incident = self.incident_repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        evidence = self.evidence_repository.get_by_id(evidence_id)

        if not evidence or evidence.incident_id != incident_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )

        content_bytes = get_evidence_content_bytes(evidence)

        return Response(
            content=content_bytes,
            media_type=evidence.content_type,
            headers={"Content-Disposition": f'inline; filename="{evidence.filename}"'}
        )
    
    def delete_evidence(self, evidence_id: UUID):
        evidence = self.evidence_repository.get_by_id(evidence_id)

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )
            
        incident = self.incident_repository.get_by_id(evidence.incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found",
            )

        if evidence.cloudinary_public_id:
            try:
                cloudinary.uploader.destroy(
                    evidence.cloudinary_public_id,
                    resource_type=evidence.cloudinary_resource_type or "raw",
                    type=evidence.cloudinary_delivery_type or "authenticated",
                    invalidate=True
                )
            except Exception as e:
                # If Cloudinary deletion fails, do not silently delete the database record
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete evidence from Cloudinary: {e}"
                )
                
        if evidence.storage_path:
            storage_path = Path(evidence.storage_path)
            if storage_path.exists():
                storage_path.unlink()

        self.evidence_repository.delete(evidence)