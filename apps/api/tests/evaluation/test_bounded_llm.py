import pytest
import time
from concurrent.futures import TimeoutError
from unittest.mock import patch, MagicMock

from app.features.investigation.agents.llm_wrapper import BoundedChatOllama

def test_bounded_chat_ollama_success():
    """Verify successful LLM calls remain unchanged."""
    llm = BoundedChatOllama(model="test-model")
    
    # Mock the super().invoke method to return immediately
    with patch("langchain_ollama.ChatOllama.invoke") as mock_invoke:
        mock_invoke.return_value = "success"
        
        result = llm.invoke("test prompt")
        assert result == "success"
        mock_invoke.assert_called_once_with("test prompt")

def test_bounded_chat_ollama_timeout():
    """Verify a simulated timeout raises/fails explicitly with the configured timeout."""
    llm = BoundedChatOllama(model="test-model")
    
    # Mock settings to return a very short timeout
    mock_settings = MagicMock()
    mock_settings.OLLAMA_TIMEOUT_SECONDS = 1
    
    def slow_invoke(*args, **kwargs):
        time.sleep(2)
        return "too late"
        
    with patch("app.features.investigation.agents.llm_wrapper.get_settings", return_value=mock_settings):
        with patch("langchain_ollama.ChatOllama.invoke", side_effect=slow_invoke):
            start = time.time()
            with pytest.raises(TimeoutError, match="LLM execution exceeded 1 seconds configured timeout"):
                llm.invoke("test prompt")
            elapsed = time.time() - start
            # Must fail close to 1 second
            assert elapsed < 1.5

@patch("app.features.investigation.service.multi_agent_graph.invoke")
def test_investigation_service_handles_timeout(mock_invoke):
    """Verify the investigation is marked FAILED through the existing error path."""
    from app.features.investigation.service import InvestigationService
    from app.features.investigation.repository import InvestigationRepository
    
    mock_db = MagicMock()
    mock_repo = MagicMock()
    
    mock_investigation = MagicMock()
    mock_investigation.status = "RUNNING"
    mock_repo.get_by_id.return_value = mock_investigation
    
    service = InvestigationService(db=mock_db, owner_id="user123")
    
    # Need to patch the repo inside run_investigation_background
    with patch("app.features.investigation.service.InvestigationRepository", return_value=mock_repo):
        with patch("app.features.investigation.service.SessionLocal", return_value=mock_db):
            with patch("app.features.investigation.service.settings") as mock_settings:
                mock_settings.MULTI_AGENT_ENABLED = True
                
                # Simulate a TimeoutError bubbling up from the multi-agent execution
                mock_invoke.side_effect = TimeoutError("LLM execution exceeded 240 seconds configured timeout")
                
                InvestigationService.run_investigation_background(mock_investigation.id, mock_investigation.incident_id, 'user123')
                
                mock_repo.mark_failed.assert_called_once_with(mock_investigation)
