import pytest
import uuid
import json
from unittest.mock import patch, MagicMock

from app.core.config import settings
from app.features.investigation.service import InvestigationService


@patch("app.features.investigation.service.InvestigationRepository")
@patch("app.features.investigation.service.SessionLocal")
@patch("app.features.investigation.service.build_investigation_graph")
@patch("app.features.investigation.service.multi_agent_graph")
def test_single_agent_workflow_selection_by_default(
    mock_multi_graph, mock_single_graph, mock_session, mock_repo
):
    """Proves flag=false selects single-agent"""
    # Ensure flag is false
    settings.MULTI_AGENT_ENABLED = False
    
    # Mock DB context
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_repo_instance = MagicMock()
    mock_repo.return_value = mock_repo_instance
    
    mock_investigation = MagicMock()
    mock_investigation.id = uuid.uuid4()
    mock_repo_instance.get_by_id.return_value = mock_investigation

    # Execute
    InvestigationService.run_investigation_background(mock_investigation.id, uuid.uuid4())
    
    # Verify Single Agent triggered
    mock_single_graph.assert_called_once()
    mock_single_graph.return_value.invoke.assert_called_once()
    
    # Verify Multi Agent ignored
    mock_multi_graph.invoke.assert_not_called()
    
    # Verify complete is NOT called here because single-agent saves internally via a node
    mock_repo_instance.complete.assert_not_called()


@patch("app.features.investigation.service.InvestigationRepository")
@patch("app.features.investigation.service.SessionLocal")
@patch("app.features.investigation.service.build_investigation_graph")
@patch("app.features.investigation.service.multi_agent_graph")
def test_multi_agent_workflow_selection_when_enabled(
    mock_multi_graph, mock_single_graph, mock_session, mock_repo
):
    """Proves flag=true selects multi-agent and persists it correctly"""
    settings.MULTI_AGENT_ENABLED = True
    
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_repo_instance = MagicMock()
    mock_repo.return_value = mock_repo_instance
    
    mock_investigation = MagicMock()
    mock_investigation.id = uuid.uuid4()
    mock_repo_instance.get_by_id.return_value = mock_investigation
    
    # Mock the return payload of the multi agent graph final node
    mock_summary_payload = {
        "summary": "Multi Agent Summary",
        "root_cause": "The multi agent cause",
        "recommendations": "Fix it",
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "missing_evidence": [],
        "hypotheses": []
    }
    
    mock_multi_graph.invoke.return_value = {
        "summary": json.dumps(mock_summary_payload)
    }

    # Execute
    InvestigationService.run_investigation_background(mock_investigation.id, uuid.uuid4())
    
    # Verify Multi Agent triggered
    mock_multi_graph.invoke.assert_called_once()
    
    # Verify Single Agent ignored
    mock_single_graph.assert_not_called()
    
    # Verify the persistence adapter correctly extracted the fields and triggered completion
    mock_repo_instance.complete.assert_called_once_with(
        mock_investigation,
        summary="Multi Agent Summary",
        root_cause="The multi agent cause",
        recommendations="Fix it",
        supporting_evidence=[],
        contradicting_evidence=[],
        missing_evidence=[],
        hypotheses=[]
    )
    
    # Clean up settings
    settings.MULTI_AGENT_ENABLED = False


@patch("app.features.investigation.service.InvestigationRepository")
@patch("app.features.investigation.service.SessionLocal")
@patch("app.features.investigation.service.multi_agent_graph")
def test_multi_agent_workflow_fails_gracefully(
    mock_multi_graph, mock_session, mock_repo
):
    """Proves that multi-agent workflow errors correctly fail the investigation"""
    settings.MULTI_AGENT_ENABLED = True
    
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_repo_instance = MagicMock()
    mock_repo.return_value = mock_repo_instance
    
    mock_investigation = MagicMock()
    mock_repo_instance.get_by_id.return_value = mock_investigation
    
    # Mock an error in the workflow execution
    mock_multi_graph.invoke.return_value = {
        "errors": ["Validation Failed in Graph"]
    }

    InvestigationService.run_investigation_background(mock_investigation.id, uuid.uuid4())
    
    # Verify failure handler triggers
    mock_repo_instance.mark_failed.assert_called_once_with(mock_investigation)
    mock_repo_instance.complete.assert_not_called()
    
    settings.MULTI_AGENT_ENABLED = False
