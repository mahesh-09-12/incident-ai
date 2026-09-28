import pytest
import uuid
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.features.investigation.service import InvestigationService
from app.features.investigation.model import Investigation
from app.features.incident.model import Incident

def test_get_investigation_success():
    mock_db = MagicMock()
    service = InvestigationService(db=mock_db, owner_id="user123")
    
    incident_id = uuid.uuid4()
    investigation_id = uuid.uuid4()
    
    # Mock incident repo to return an incident (meaning it's owned by the user, as the repo is scoped)
    mock_incident = MagicMock(spec=Incident)
    mock_incident.id = incident_id
    service.incident_repository.get_by_id = MagicMock(return_value=mock_incident)
    
    # Mock investigation repo
    mock_investigation = MagicMock(spec=Investigation)
    mock_investigation.id = investigation_id
    mock_investigation.incident_id = incident_id
    service.investigation_repository.get_by_id = MagicMock(return_value=mock_investigation)
    
    result = service.get_investigation(incident_id, investigation_id)
    assert result == mock_investigation

def test_get_investigation_wrong_owner():
    mock_db = MagicMock()
    service = InvestigationService(db=mock_db, owner_id="user123")
    
    incident_id = uuid.uuid4()
    investigation_id = uuid.uuid4()
    
    # Mock incident repo to return None (meaning it doesn't belong to the owner)
    service.incident_repository.get_by_id = MagicMock(return_value=None)
    
    with pytest.raises(HTTPException) as exc:
        service.get_investigation(incident_id, investigation_id)
        
    assert exc.value.status_code == 404
    assert exc.value.detail == "Investigation not found"
