import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.features.investigation.multi_agent_contracts import (
    MultiAgentInvestigationState,
    Observation,
    MultiAgentHypothesis,
    ValidationFinding,
    RecommendationResult,
)
from app.features.investigation.schema import EvidenceReference
from app.features.investigation.timeline import TimelineEvent
from app.features.investigation.multi_agent_workflow import (
    load_incident_data,
    build_timeline_node,
    finalize_result,
    multi_agent_graph,
    MultiAgentContext,
)


@pytest.fixture
def mock_db_context():
    # Setup mocks for load_incident_data
    mock_db = MagicMock()
    
    mock_incident = MagicMock()
    mock_incident.id = uuid.uuid4()
    mock_incident.title = "Test Incident"
    mock_incident.description = "Test Desc"
    mock_incident.severity = "high"
    mock_incident.environment = "prod"
    mock_incident.service = "api"
    mock_incident.status = "open"
    
    mock_incident_repo = MagicMock()
    mock_incident_repo.get_by_id.return_value = mock_incident
    
    mock_evidence = MagicMock()
    mock_evidence.id = uuid.uuid4()
    mock_evidence.filename = "test.log"
    mock_evidence.content_type = "text/plain"
    mock_evidence.file_size = 100
    mock_evidence.storage_path = "mock/path.log"
    
    mock_evidence_repo = MagicMock()
    mock_evidence_repo.list_by_incident.return_value = [mock_evidence]
    
    return {
        "db": mock_db,
        "incident_repo": mock_incident_repo,
        "evidence_repo": mock_evidence_repo,
        "evidence_mock": mock_evidence
    }


def test_finalize_result_success():
    state: MultiAgentInvestigationState = {
        "investigation_id": uuid.uuid4(),
        "incident_id": uuid.uuid4(),
        "incident_context": {},
        "evidence_payload": [],
        "timeline": [],
        "observations": [
            Observation(description="test", evidence_id="ev1", timeline_event_ids=[])
        ],
        "hypotheses": [
            MultiAgentHypothesis(
                id="H-1", hypothesis="Test Root Cause", reasoning="",
                supporting_evidence=[EvidenceReference(evidence_id="ev1", filename="test.log", explanation="")],
                contradicting_evidence=[], missing_evidence=[],
                immediate_mitigations=["Reboot"], preventative_measures=["Scale"]
            )
        ],
        "validation_findings": [],
        "ranking": [
            MagicMock(hypothesis_id="H-1", rank=1, confidence_rationale="Winner")
        ],
        "recommendations": RecommendationResult(immediate_mitigations=["Reboot"], preventative_measures=["Scale"]),
        "summary": None,
        "errors": []
    }
    
    result = finalize_result(state)
    assert "summary" in result
    assert "Test Root Cause" in result["summary"] # Check json dump containing root cause


def test_finalize_result_with_errors_fails():
    state = {"errors": ["A deterministic error occurred in a previous node!"]}
    with pytest.raises(ValueError, match="Graph execution failed with errors"):
        finalize_result(state)


def test_finalize_result_missing_data_fails():
    state = {"errors": [], "ranking": [], "hypotheses": [MagicMock()], "recommendations": None}
    with pytest.raises(ValueError, match="Cannot finalize result"):
        finalize_result(state)

def test_finalize_result_no_hypotheses_success():
    state = {
        "errors": [],
        "observations": [],
        "hypotheses": [],
        "ranking": [],
        "recommendations": RecommendationResult(
            immediate_mitigations=["No immediate mitigations could be generated."],
            preventative_measures=["No preventative measures could be generated."]
        )
    }
    result = finalize_result(state)
    assert "summary" in result
    assert "No root cause identified" in result["summary"]


@patch("app.features.investigation.multi_agent_workflow.IncidentRepository")
@patch("app.features.investigation.multi_agent_workflow.EvidenceRepository")
@patch("app.features.investigation.multi_agent_workflow.Path")
def test_load_incident_data(mock_path, mock_ev_repo, mock_inc_repo, mock_db_context):
    mock_inc_repo.return_value = mock_db_context["incident_repo"]
    mock_ev_repo.return_value = mock_db_context["evidence_repo"]
    
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.read_text.return_value = "timeout log entry"
    mock_path.return_value = mock_path_instance
    
    state = {"incident_id": uuid.uuid4()}
    runtime = MagicMock(context=MultiAgentContext(db=mock_db_context["db"]))
    
    result = load_incident_data(state, runtime)
    
    assert "incident_context" in result
    assert result["incident_context"]["title"] == "Test Incident"
    
    assert "evidence_payload" in result
    assert len(result["evidence_payload"]) == 1
    assert result["evidence_payload"][0]["content"] == "timeout log entry"
