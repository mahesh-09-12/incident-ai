import time
from uuid import UUID

from app.db.session import SessionLocal
from app.core.config import settings
from app.features.incident.repository import IncidentRepository
from app.features.investigation.repository import InvestigationRepository
from app.features.evidence.repository import EvidenceRepository
from app.features.investigation.service import InvestigationService
from tests.evaluation.evaluator import evaluate_investigation
import json

def run_smoke_test():
    # Force Multi-Agent On
    settings.MULTI_AGENT_ENABLED = True
    print("[TEST] MULTI_AGENT_ENABLED =", settings.MULTI_AGENT_ENABLED)

    db = SessionLocal()
    try:
        incident_repo = IncidentRepository(db)
        evidence_repo = EvidenceRepository(db)
        investigation_repo = InvestigationRepository(db)
        
        # Find an incident with evidence
        all_incidents = incident_repo.list()
        target_incident = None
        for inc in all_incidents:
            evidences = evidence_repo.list_by_incident(inc.id)
            if len(evidences) > 1:
                target_incident = inc
                break
                
        if not target_incident:
            for inc in all_incidents:
                evidences = evidence_repo.list_by_incident(inc.id)
                if len(evidences) > 0:
                    target_incident = inc
                    break
                
        if not target_incident:
            print("[TEST] Could not find any incident with evidence.")
            return
            
        print(f"[TEST] Using Incident: {target_incident.id} ({target_incident.title})")
        
        # Create an investigation
        investigation = investigation_repo.create(incident_id=target_incident.id)
        investigation_repo.mark_running(investigation)
        print(f"[TEST] Created Investigation: {investigation.id}")
        
        # Start timer
        start_time = time.time()
        
        # Run it synchronously
        print("[TEST] Starting Multi-Agent Execution...")
        InvestigationService.run_investigation_background(investigation.id, target_incident.id)
        
        execution_time = time.time() - start_time
        print(f"[TEST] Execution Completed in {execution_time:.2f} seconds.")
        
        # Refresh investigation from DB
        db.refresh(investigation)
        print(f"[TEST] Final Status: {investigation.status}")
        
        if investigation.status == "FAILED":
            print("[TEST] Investigation Failed!")
            return
            
        if investigation.status == "COMPLETED":
            # Extract structured result
            print("\n[TEST] Summary Output:")
            print(investigation.summary)
            
            print("\n[TEST] Root Cause:")
            print(investigation.root_cause)
            
            # Re-parse state for the evaluator
            evidence_items = evidence_repo.list_by_incident(target_incident.id)
            supplied_ids = {str(e.id) for e in evidence_items}
            
            # Format state correctly for the evaluator
            final_state = {
                "summary": json.dumps({
                    "summary": investigation.summary,
                    "root_cause": investigation.root_cause,
                    "recommendations": investigation.recommendations,
                    "supporting_evidence": investigation.supporting_evidence,
                    "contradicting_evidence": investigation.contradicting_evidence,
                    "missing_evidence": investigation.missing_evidence,
                    "hypotheses": investigation.hypotheses
                })
            }
            
            metrics = evaluate_investigation(final_state, supplied_ids)
            
            print("\n[TEST] Evaluator Metrics:")
            print(f"- Schema Compliant: {metrics.is_schema_compliant}")
            print(f"- Evidence Grounded: {metrics.is_grounded}")
            print(f"- Has Valid Hypotheses: {metrics.has_valid_hypotheses}")
            print(f"- Is Traceable: {metrics.is_traceable}")
            print(f"- Overall Score: {metrics.score:.2f}")

    finally:
        db.close()
        # Restore configuration
        settings.MULTI_AGENT_ENABLED = False
        print("[TEST] Restored MULTI_AGENT_ENABLED = False")


if __name__ == "__main__":
    run_smoke_test()
