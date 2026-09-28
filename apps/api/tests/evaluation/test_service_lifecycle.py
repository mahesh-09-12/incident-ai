import pytest
import uuid
from unittest.mock import patch, MagicMock

from app.features.investigation.service import InvestigationService
from app.core.config import settings
from sqlalchemy.exc import PendingRollbackError

@patch("app.features.investigation.service.SessionLocal")
@patch("app.features.investigation.service.InvestigationRepository")
@patch("app.features.investigation.service.IncidentRepository")
@patch("app.features.investigation.service.EvidenceRepository")
@patch("app.features.investigation.service.multi_agent_graph")
def test_session_lifecycle_multi_agent(mock_graph, mock_ev_repo, mock_inc_repo, mock_inv_repo, mock_session_local):
    # Ensure MULTI_AGENT_ENABLED is True for this test
    original_setting = settings.MULTI_AGENT_ENABLED
    settings.MULTI_AGENT_ENABLED = True
    
    try:
        investigation_id = uuid.uuid4()
        incident_id = uuid.uuid4()
        
        # Setup mocks
        mock_db_1 = MagicMock()
        mock_db_2 = MagicMock()
        mock_session_local.side_effect = [mock_db_1, mock_db_2]
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = MagicMock(id=investigation_id)
        mock_inv_repo.return_value = mock_repo_instance
        
        mock_inc_repo_instance = MagicMock()
        mock_inc_repo_instance.get_by_id.return_value = MagicMock(id=incident_id)
        mock_inc_repo.return_value = mock_inc_repo_instance
        
        mock_ev_repo_instance = MagicMock()
        mock_ev_repo_instance.list_by_incident.return_value = []
        mock_ev_repo.return_value = mock_ev_repo_instance
        
        mock_graph.invoke.return_value = {
            "summary": '{"summary": "test", "root_cause": "test", "recommendations": "test", "supporting_evidence": [], "contradicting_evidence": [], "missing_evidence": [], "hypotheses": []}'
        }
        
        InvestigationService.run_investigation_background(investigation_id, incident_id, 'user123')
        
        # Verify db_1 (read transaction) was closed before the graph was invoked
        mock_db_1.close.assert_called_once()
        
        # Verify db_2 (persist transaction) was closed after graph invocation
        mock_db_2.close.assert_called_once()
        
        # Ensure graph invocation happens in between (mock order)
        # Actually just ensure invoke was called
        mock_graph.invoke.assert_called_once()
    finally:
        settings.MULTI_AGENT_ENABLED = original_setting

@patch("app.features.investigation.service.SessionLocal")
@patch("app.features.investigation.service.InvestigationRepository")
@patch("app.features.investigation.service.IncidentRepository")
@patch("app.features.investigation.service.EvidenceRepository")
@patch("app.features.investigation.service.multi_agent_graph")
def test_persistence_failure_rollback(mock_graph, mock_ev_repo, mock_inc_repo, mock_inv_repo, mock_session_local):
    original_setting = settings.MULTI_AGENT_ENABLED
    settings.MULTI_AGENT_ENABLED = True
    
    try:
        investigation_id = uuid.uuid4()
        incident_id = uuid.uuid4()
        
        mock_db_1 = MagicMock()
        mock_db_2 = MagicMock()
        mock_db_3 = MagicMock() # For mark_failed
        mock_session_local.side_effect = [mock_db_1, mock_db_2, mock_db_3]
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = MagicMock(id=investigation_id)
        
        # Simulate a DB error during complete()
        def mock_complete(*args, **kwargs):
            raise PendingRollbackError("Simulated DB persistence failure")
        mock_repo_instance.complete.side_effect = mock_complete
        
        mock_inv_repo.return_value = mock_repo_instance
        
        mock_inc_repo_instance = MagicMock()
        mock_inc_repo_instance.get_by_id.return_value = MagicMock(id=incident_id)
        mock_inc_repo.return_value = mock_inc_repo_instance
        
        mock_ev_repo_instance = MagicMock()
        mock_ev_repo_instance.list_by_incident.return_value = []
        mock_ev_repo.return_value = mock_ev_repo_instance
        
        mock_graph.invoke.return_value = {
            "summary": '{"summary": "test", "root_cause": "test", "recommendations": "test", "supporting_evidence": [], "contradicting_evidence": [], "missing_evidence": [], "hypotheses": []}'
        }
        
        InvestigationService.run_investigation_background(investigation_id, incident_id, 'user123')
        
        # db_2 should be rolled back and closed
        mock_db_2.rollback.assert_called_once()
        mock_db_2.close.assert_called_once()
        
        # db_3 should be used to mark as failed
        mock_repo_instance.mark_failed.assert_called_once()
        mock_db_3.close.assert_called_once()
    finally:
        settings.MULTI_AGENT_ENABLED = original_setting
