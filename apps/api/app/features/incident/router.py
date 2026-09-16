from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.incident.schema import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.features.incident.service import IncidentService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.create_incident(incident)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.list_incidents(
        skip=skip,
        limit=limit,
        severity=severity,
        status=status,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.get_incident(incident_id)


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident(
    incident_id: UUID,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.update_incident(
        incident_id,
        data,
    )


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    service.delete_incident(incident_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)