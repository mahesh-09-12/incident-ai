from uuid import UUID

from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.features.incident.repository import IncidentRepository
from app.features.investigation.repository import InvestigationRepository
from app.features.evidence.repository import EvidenceRepository

from app.core.config import settings
import json

from app.features.investigation.workflow import (
    InvestigationContext,
    build_investigation_graph,
)
from app.features.investigation.multi_agent_workflow import (
    multi_agent_graph,
    MultiAgentContext,
)


class InvestigationService:
    def __init__(self, db: Session):
        self.investigation_repository = InvestigationRepository(db)
        self.incident_repository = IncidentRepository(db)
        self.evidence_repository = EvidenceRepository(db)

    def create_investigation(self, incident_id: UUID, background_tasks: BackgroundTasks):
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

        background_tasks.add_task(
            self.run_investigation_background,
            investigation.id,
            incident_id,
        )

        return investigation

    @staticmethod
    def run_investigation_background(investigation_id: UUID, incident_id: UUID):
        try:
            if settings.MULTI_AGENT_ENABLED:
                db = SessionLocal()
                try:
                    repo = InvestigationRepository(db)
                    investigation = repo.get_by_id(investigation_id)
                    if not investigation:
                        return
                    
                    incident_repo = IncidentRepository(db)
                    evidence_repo = EvidenceRepository(db)
                    incident = incident_repo.get_by_id(incident_id)
                    if not incident:
                        raise Exception("Incident not found")
                    
                    incident_context = {
                        "id": str(incident.id),
                        "title": incident.title,
                        "description": incident.description,
                        "severity": incident.severity,
                        "environment": incident.environment,
                        "service": incident.service,
                        "status": incident.status,
                    }

                    from pathlib import Path
                    evidence_items = evidence_repo.list_by_incident(incident_id)
                    evidence_payload = []
                    for item in evidence_items:
                        path = Path(item.storage_path)
                        if not path.exists():
                            raise Exception(f"Evidence file not found: {item.filename}")
                        content = path.read_text(encoding="utf-8", errors="replace")
                        evidence_payload.append({
                            "id": str(item.id),
                            "filename": item.filename,
                            "content_type": item.content_type,
                            "file_size": item.file_size,
                            "storage_path": item.storage_path,
                            "content": content,
                        })
                finally:
                    db.close()
                
                initial_state = {
                    "investigation_id": investigation_id,
                    "incident_id": incident_id,
                    "incident_context": incident_context,
                    "evidence_payload": evidence_payload,
                    "timeline": [],
                    "observations": [],
                    "hypotheses": [],
                    "validation_findings": [],
                    "ranking": [],
                    "recommendations": None,
                    "summary": None,
                    "errors": [],
                    "warnings": []
                }
                
                final_state = multi_agent_graph.invoke(
                    initial_state,
                    context=MultiAgentContext(db=None),
                )
                
                if final_state.get("errors"):
                    raise Exception(f"Multi-agent workflow failed: {'; '.join(final_state['errors'])}")
                    
                summary_data = json.loads(final_state["summary"])
                
                db_persist = SessionLocal()
                try:
                    repo_persist = InvestigationRepository(db_persist)
                    investigation_persist = repo_persist.get_by_id(investigation_id)
                    if investigation_persist:
                        repo_persist.complete(
                            investigation_persist,
                            summary=summary_data.get("summary", ""),
                            root_cause=summary_data.get("root_cause", ""),
                            recommendations=summary_data.get("recommendations", ""),
                            supporting_evidence=summary_data.get("supporting_evidence", []),
                            contradicting_evidence=summary_data.get("contradicting_evidence", []),
                            missing_evidence=summary_data.get("missing_evidence", []),
                            hypotheses=summary_data.get("hypotheses", []),
                        )
                except Exception as e:
                    db_persist.rollback()
                    raise e
                finally:
                    db_persist.close()
                    
            else:
                db = SessionLocal()
                try:
                    repo = InvestigationRepository(db)
                    investigation = repo.get_by_id(investigation_id)
                    if not investigation:
                        return
                        
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
                        "supporting_evidence": None,
                        "contradicting_evidence": None,
                        "missing_evidence": None,
                        "hypotheses": None,
                        "error": None,
                    }
        
                    graph.invoke(
                        initial_state,
                        context=InvestigationContext(
                            db=db
                        ),
                    )
                finally:
                    db.close()
        except Exception as e:
            print(f"Exception during run_investigation_background: {e}")
            db_fail = SessionLocal()
            try:
                repo_fail = InvestigationRepository(db_fail)
                investigation_fail = repo_fail.get_by_id(investigation_id)
                if investigation_fail:
                    repo_fail.mark_failed(investigation_fail)
            except Exception as fail_e:
                print(f"Failed to mark as failed: {fail_e}")
            finally:
                db_fail.close()
    
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