import pytest
from unittest.mock import patch, MagicMock
from app.features.investigation.agents.llm_wrapper import get_llm, BoundedChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import Settings

@pytest.fixture
def mock_settings():
    with patch("app.features.investigation.agents.llm_wrapper.get_settings") as mock:
        settings = Settings(
            DATABASE_URL="sqlite:///:memory:",
            SECRET_KEY="test",
            AI_PROVIDER="ollama"
        )
        mock.return_value = settings
        yield mock

def test_get_llm_default_ollama(mock_settings):
    llm = get_llm(temperature=0.5)
    assert isinstance(llm, BoundedChatOllama)
    assert llm.model == "qwen3:4b"
    assert llm.temperature == 0.5

def test_get_llm_gemini_success(mock_settings):
    mock_settings.return_value.AI_PROVIDER = "gemini"
    mock_settings.return_value.GEMINI_API_KEY = "test_key"
    mock_settings.return_value.GEMINI_MODEL = "gemini-test-model"
    
    llm = get_llm(temperature=0.2)
    assert isinstance(llm, ChatGoogleGenerativeAI)
    assert llm.model == "gemini-test-model"
    assert llm.temperature == 0.2

def test_get_llm_gemini_missing_api_key(mock_settings):
    mock_settings.return_value.AI_PROVIDER = "gemini"
    mock_settings.return_value.GEMINI_API_KEY = ""
    
    with pytest.raises(ValueError, match="GEMINI_API_KEY must be configured when AI_PROVIDER is 'gemini'"):
        get_llm()

def test_agent_compatibility_with_structured_output(mock_settings):
    llm = get_llm()
    assert hasattr(llm, "with_structured_output")
    
    mock_settings.return_value.AI_PROVIDER = "gemini"
    mock_settings.return_value.GEMINI_API_KEY = "test_key"
    gemini_llm = get_llm()
    assert hasattr(gemini_llm, "with_structured_output")

def test_get_llm_invalid_provider(mock_settings):
    mock_settings.return_value.AI_PROVIDER = "invalid_provider"
    
    with pytest.raises(ValueError, match="Invalid AI_PROVIDER: 'invalid_provider'. Supported providers are 'ollama' and 'gemini'."):
        get_llm()
