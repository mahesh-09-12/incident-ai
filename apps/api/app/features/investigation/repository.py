from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.investigation.model import Investigation


class InvestigationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, incident_id: UUID) -> Investigation:
        investigation = Investigation(
            incident_id=incident_id,
        )

        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)

        return investigation

    def get_by_id(
        self,
        investigation_id: UUID,
    ) -> Investigation | None:
        statement = select(Investigation).where(
            Investigation.id == investigation_id
        )

        return self.db.scalar(statement)

    def list_by_incident(
        self,
        incident_id: UUID,
    ) -> list[Investigation]:
        statement = (
            select(Investigation)
            .where(Investigation.incident_id == incident_id)
            .order_by(Investigation.created_at.desc())
        )

        return list(self.db.scalars(statement).all())
    
    def mark_running(
        self,
        investigation: Investigation,
    ) -> Investigation:
        investigation.status = "RUNNING"

        self.db.commit()
        self.db.refresh(investigation)

        return investigation
    
    def complete(
        self,
        investigation: Investigation,
        *,
        summary: str,
        root_cause: str,
        recommendations: str,
        supporting_evidence: list[dict] | None = None,
        contradicting_evidence: list[dict] | None = None,
        missing_evidence: list[str] | None = None,
        hypotheses: list[dict] | None = None,
    ) -> Investigation:
        investigation.status = "COMPLETED"
        investigation.summary = summary
        investigation.root_cause = root_cause
        investigation.recommendations = recommendations
        investigation.supporting_evidence = supporting_evidence
        investigation.contradicting_evidence = contradicting_evidence
        investigation.missing_evidence = missing_evidence
        investigation.hypotheses = hypotheses
        investigation.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(investigation)

        return investigation
    
    def mark_failed(
        self,
        investigation: Investigation,
    ) -> Investigation:
        investigation.status = "FAILED"

        self.db.commit()
        self.db.refresh(investigation)

        return investigation