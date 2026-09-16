from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.investigation.schema import InvestigationResponse
from app.features.investigation.service import InvestigationService

router = APIRouter(
    prefix="/incidents/{incident_id}/investigations",
    tags=["Investigations"],
)


@router.post(
    "",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_investigation(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    service = InvestigationService(db)

    return service.create_investigation(incident_id)


@router.get(
    "",
    response_model=list[InvestigationResponse],
)
def list_investigations(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    service = InvestigationService(db)

    return service.list_investigations(incident_id)

@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    incident_id: UUID,
    investigation_id: UUID,
    db: Session = Depends(get_db),
):
    service = InvestigationService(db)

    return service.get_investigation(
        incident_id,
        investigation_id,
    )