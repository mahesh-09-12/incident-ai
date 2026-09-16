from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.incident.repository import IncidentRepository
from app.features.investigation.repository import InvestigationRepository
from app.features.evidence.repository import EvidenceRepository

from app.features.investigation.workflow import (
    InvestigationContext,
    build_investigation_graph,
)


class InvestigationService:
    def __init__(self, db: Session):
        self.investigation_repository = InvestigationRepository(db)
        self.incident_repository = IncidentRepository(db)
        self.evidence_repository = EvidenceRepository(db)

    def create_investigation(self, incident_id: UUID):
        incident = self.incident_repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        evidence = self.evidence_repository.list_by_incident(
            incident_id
        )

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one evidence file is required to start an investigation",
            )

        investigation = self.investigation_repository.create(
            incident_id=incident_id,
        )

        self.investigation_repository.mark_running(
            investigation
        )

        graph = build_investigation_graph()

        initial_state = {
            "investigation_id": investigation.id,
            "incident_id": incident_id,
            "incident": None,
            "evidence": [],
            "analysis": None,
            "summary": None,
            "root_cause": None,
            "recommendations": None,
            "error": None,
        }

        try:
            graph.invoke(
                initial_state,
                context=InvestigationContext(
                    db=self.investigation_repository.db
                ),
            )
        except Exception:
            self.investigation_repository.mark_failed(
                investigation
            )
            raise

        return investigation
    
    def get_investigation(
        self,
        incident_id: UUID,
        investigation_id: UUID,
    ):
        investigation = self.investigation_repository.get_by_id(
            investigation_id
        )

        if not investigation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )

        if investigation.incident_id != incident_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )

        return investigation

    def list_investigations(self, incident_id: UUID):
        incident = self.incident_repository.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return self.investigation_repository.list_by_incident(
            incident_id
        )