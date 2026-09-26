import pytest
import logging
from unittest.mock import patch, MagicMock

from app.features.investigation.multi_agent_workflow import with_observability

def dummy_node(state: dict) -> dict:
    return {"updated": True}

def dummy_node_raises(state: dict) -> dict:
    raise ValueError("Test error")

def dummy_node_with_runtime(state: dict, runtime: object) -> dict:
    return {"state": state, "runtime": runtime}

def test_with_observability_success(caplog):
    caplog.set_level(logging.INFO)
    wrapped_node = with_observability("dummy_node")(dummy_node)
    
    result = wrapped_node({"test": "data"})
    
    # Verify state updates are preserved
    assert result == {"updated": True}
    
    # Verify logging
    logs = [rec.message for rec in caplog.records if "MultiAgent" in rec.message]
    assert len(logs) == 2
    assert logs[0] == "[MultiAgent] START dummy_node"
    assert "[MultiAgent] END dummy_node elapsed=" in logs[1]

def test_with_observability_failure(caplog):
    caplog.set_level(logging.INFO)
    wrapped_node = with_observability("dummy_node_raises")(dummy_node_raises)
    
    with pytest.raises(ValueError, match="Test error"):
        wrapped_node({"test": "data"})
        
    logs = [rec.message for rec in caplog.records if "MultiAgent" in rec.message]
    assert len(logs) == 2
    assert logs[0] == "[MultiAgent] START dummy_node_raises"
    assert "[MultiAgent] ERROR dummy_node_raises elapsed=" in logs[1]
    assert "error=Test error" in logs[1]

def test_with_observability_preserves_signature(caplog):
    caplog.set_level(logging.INFO)
    wrapped_node = with_observability("dummy_node_with_runtime")(dummy_node_with_runtime)
    
    runtime_mock = MagicMock()
    result = wrapped_node({"test": "data"}, runtime_mock)
    
    # Verify arguments pass through correctly
    assert result["state"] == {"test": "data"}
    assert result["runtime"] == runtime_mock
    
    logs = [rec.message for rec in caplog.records if "MultiAgent" in rec.message]
    assert len(logs) == 2
    assert logs[0] == "[MultiAgent] START dummy_node_with_runtime"
    assert "[MultiAgent] END dummy_node_with_runtime elapsed=" in logs[1]
