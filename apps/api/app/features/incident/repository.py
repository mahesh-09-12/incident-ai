from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.incident.model import Incident
from app.features.incident.schema import IncidentCreate, IncidentUpdate


class IncidentRepository:
    def __init__(self, db: Session, owner_id: str):
        self.db = db
        self.owner_id = owner_id

    def create(self, incident: IncidentCreate) -> Incident:
        db_incident = Incident(
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            environment=incident.environment,
            service=incident.service,
            owner_id=self.owner_id,
        )

        self.db.add(db_incident)
        self.db.commit()
        self.db.refresh(db_incident)

        return db_incident

    def get_by_id(self, incident_id: UUID) -> Incident | None:
        statement = select(Incident).where(
            Incident.id == incident_id,
            Incident.owner_id == self.owner_id
        )
        return self.db.scalar(statement)

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        severity: str | None = None,
        status: str | None = None,
    ) -> list[Incident]:
        statement = select(Incident).where(Incident.owner_id == self.owner_id)

        if severity:
            statement = statement.where(Incident.severity == severity)

        if status:
            statement = statement.where(Incident.status == status)

        statement = (
            statement
            .order_by(Incident.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        incident: Incident,
        data: IncidentUpdate,
    ) -> Incident:
        update_data = data.model_dump(exclude_unset=True)
        print("UPDATE DATA:", update_data)

        for field, value in update_data.items():
            setattr(incident, field, value)

        self.db.commit()
        self.db.refresh(incident)

        return incident

    def delete(self, incident: Incident) -> None:
        self.db.delete(incident)
        self.db.commit()