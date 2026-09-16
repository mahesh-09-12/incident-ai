from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.evidence.schema import EvidenceResponse
from app.features.evidence.service import EvidenceService

router = APIRouter(
    prefix="/incidents/{incident_id}/evidence",
    tags=["Evidence"],
)


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_evidence(
    incident_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)

    return await service.upload_evidence(
        incident_id=incident_id,
        file=file,
    )

@router.get(
    "",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)

    return service.list_evidence(incident_id)

@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)

    return service.get_evidence(evidence_id)

@router.delete(
    "/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)

    service.delete_evidence(evidence_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)