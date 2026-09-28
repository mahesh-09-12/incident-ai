from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.incident.repository import IncidentRepository
from app.features.incident.schema import IncidentCreate, IncidentUpdate


class IncidentService:
    def __init__(self, db: Session, owner_id: str):
        self.repository = IncidentRepository(db, owner_id)

    def create_incident(self, incident: IncidentCreate):
        return self.repository.create(incident)

    def get_incident(self, incident_id: UUID):
        incident = self.repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return incident

    def list_incidents(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        severity: str | None = None,
        status: str | None = None,
    ):
        return self.repository.list(
            skip=skip,
            limit=limit,
            severity=severity,
            status=status,
        )

    def update_incident(
        self,
        incident_id: UUID,
        data: IncidentUpdate,
    ):
        incident = self.get_incident(incident_id)

        return self.repository.update(incident, data)

    def delete_incident(self, incident_id: UUID):
        incident = self.get_incident(incident_id)

        self.repository.delete(incident)