import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from app.core.config import settings
from app.features.evidence.model import Evidence
from app.features.evidence.service import EvidenceService
from app.features.evidence.storage import get_evidence_content_bytes

class DummyFile:
    def __init__(self, filename="test.txt", content_type="text/plain"):
        self.filename = filename
        self.content_type = content_type
    async def read(self):
        return b"hello world"

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_incident_repo():
    with patch("app.features.evidence.service.IncidentRepository") as mock:
        yield mock

@pytest.fixture
def mock_evidence_repo():
    with patch("app.features.evidence.service.EvidenceRepository") as mock:
        yield mock

@pytest.mark.anyio
async def test_upload_evidence_cloudinary_success(mock_db, mock_incident_repo, mock_evidence_repo):
    with patch("app.features.evidence.service.settings") as mock_settings:
        mock_settings.is_cloudinary_enabled = True
        
        service = EvidenceService(mock_db, "user123")
        incident_id = uuid4()
        
        # Mock incident exists
        service.incident_repository.get_by_id.return_value = MagicMock()
        
        # Mock evidence repo create
        mock_created = MagicMock()
        service.evidence_repository.create.return_value = mock_created
        
        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = {
                "public_id": "test_public_id",
                "asset_id": "test_asset_id",
                "resource_type": "raw",
                "type": "authenticated"
            }
            
            result = await service.upload_evidence(incident_id, DummyFile())
            
            mock_upload.assert_called_once()
            service.evidence_repository.create.assert_called_once()
            
            kwargs = service.evidence_repository.create.call_args[1]
            assert kwargs["cloudinary_public_id"] == "test_public_id"
            assert kwargs["storage_path"] is None
            assert result == mock_created

@pytest.mark.anyio
async def test_upload_evidence_cloudinary_failure(mock_db, mock_incident_repo, mock_evidence_repo):
    with patch("app.features.evidence.service.settings") as mock_settings:
        mock_settings.is_cloudinary_enabled = True
        
        service = EvidenceService(mock_db, "user123")
        incident_id = uuid4()
        
        service.incident_repository.get_by_id.return_value = MagicMock()
        
        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.side_effect = Exception("Cloudinary Error")
            
            with pytest.raises(HTTPException) as exc:
                await service.upload_evidence(incident_id, DummyFile())
            
            assert exc.value.status_code == 500
            assert "Failed to upload evidence to Cloudinary" in str(exc.value.detail)

def test_delete_evidence_cloudinary_success(mock_db, mock_incident_repo, mock_evidence_repo):
    service = EvidenceService(mock_db, "user123")
    evidence_id = uuid4()
    
    mock_evidence = MagicMock()
    mock_evidence.incident_id = uuid4()
    mock_evidence.cloudinary_public_id = "test_public_id"
    mock_evidence.cloudinary_resource_type = "raw"
    mock_evidence.cloudinary_delivery_type = "authenticated"
    mock_evidence.storage_path = None
    
    service.evidence_repository.get_by_id.return_value = mock_evidence
    service.incident_repository.get_by_id.return_value = MagicMock()
    
    with patch("cloudinary.uploader.destroy") as mock_destroy:
        service.delete_evidence(evidence_id)
        mock_destroy.assert_called_once_with(
            "test_public_id",
            resource_type="raw",
            type="authenticated",
            invalidate=True
        )
        service.evidence_repository.delete.assert_called_once_with(mock_evidence)

def test_delete_evidence_cloudinary_failure(mock_db, mock_incident_repo, mock_evidence_repo):
    service = EvidenceService(mock_db, "user123")
    evidence_id = uuid4()
    
    mock_evidence = MagicMock()
    mock_evidence.incident_id = uuid4()
    mock_evidence.cloudinary_public_id = "test_public_id"
    mock_evidence.storage_path = None
    
    service.evidence_repository.get_by_id.return_value = mock_evidence
    service.incident_repository.get_by_id.return_value = MagicMock()
    
    with patch("cloudinary.uploader.destroy") as mock_destroy:
        mock_destroy.side_effect = Exception("Cloudinary Error")
        
        with pytest.raises(HTTPException) as exc:
            service.delete_evidence(evidence_id)
            
        assert exc.value.status_code == 500
        assert "Failed to delete evidence from Cloudinary" in str(exc.value.detail)
        service.evidence_repository.delete.assert_not_called()

def test_get_evidence_content_cloudinary():
    evidence = Evidence(
        cloudinary_public_id="test_public_id",
        cloudinary_resource_type="raw",
        cloudinary_delivery_type="authenticated",
        storage_path=None
    )
    
    with patch("app.features.evidence.storage.settings") as mock_settings:
        mock_settings.is_cloudinary_enabled = True
        
        with patch("cloudinary.utils.cloudinary_url") as mock_url:
            mock_url.return_value = ("http://signed-url", {})
            
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b"cloud content"
                mock_urlopen.return_value.__enter__.return_value = mock_response
                
                result = get_evidence_content_bytes(evidence)
                
                assert result == b"cloud content"
                mock_url.assert_called_once_with(
                    "test_public_id",
                    resource_type="raw",
                    type="authenticated",
                    sign_url=True
                )

def test_get_evidence_content_cloudinary_unauthorized():
    evidence = Evidence(
        cloudinary_public_id="test_public_id",
        storage_path=None
    )
    
    with patch("app.features.evidence.storage.settings") as mock_settings:
        mock_settings.is_cloudinary_enabled = True
        
        with patch("cloudinary.utils.cloudinary_url") as mock_url:
            mock_url.return_value = ("http://signed-url", {})
            
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_urlopen.side_effect = Exception("HTTP 401")
                
                with pytest.raises(HTTPException) as exc:
                    get_evidence_content_bytes(evidence)
                    
                assert exc.value.status_code == 500

def test_get_evidence_content_missing_config():
    evidence = Evidence(
        cloudinary_public_id="test_public_id",
        storage_path=None
    )
    
    with patch("app.features.evidence.storage.settings") as mock_settings:
        mock_settings.is_cloudinary_enabled = False
        
        with pytest.raises(HTTPException) as exc:
            get_evidence_content_bytes(evidence)
            
        assert exc.value.status_code == 500
        assert "Cloudinary is not enabled" in str(exc.value.detail)

def test_config_validation():
    from app.core.config import Settings
    
    with pytest.raises(ValueError):
        Settings(STORAGE_PROVIDER="cloudinary", CLOUDINARY_CLOUD_NAME="")

def test_evidence_response_serialization():
    from app.features.evidence.schema import EvidenceResponse
    from datetime import datetime
    
    # Test local storage
    local_data = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "filename": "local.txt",
        "content_type": "text/plain",
        "file_size": 1024,
        "storage_path": "/local/path.txt",
        "created_at": datetime.now()
    }
    local_response = EvidenceResponse(**local_data)
    assert local_response.storage_path == "/local/path.txt"
    assert local_response.cloudinary_public_id is None
    
    # Test Cloudinary storage
    cloud_data = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "filename": "cloud.txt",
        "content_type": "text/plain",
        "file_size": 2048,
        "storage_path": None,
        "cloudinary_public_id": "public_id_123",
        "cloudinary_asset_id": "asset_id_456",
        "cloudinary_resource_type": "raw",
        "cloudinary_delivery_type": "authenticated",
        "created_at": datetime.now()
    }
    cloud_response = EvidenceResponse(**cloud_data)
    assert cloud_response.storage_path is None
    assert cloud_response.cloudinary_public_id == "public_id_123"
    assert cloud_response.cloudinary_asset_id == "asset_id_456"
