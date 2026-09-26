import pytest
from pydantic import ValidationError
import uuid
from datetime import datetime, timezone

from app.features.investigation.multi_agent_contracts import (
    Observation,
    MultiAgentHypothesis,
    ValidationFinding,
    RankedHypothesis,
    RecommendationResult,
)
from app.features.investigation.timeline import TimelineEvent


def test_valid_state_models():
    """Verify all models can be cleanly instantiated with correct data."""
    obs = Observation(
        description="CPU spiked to 100%",
        evidence_id="ev-123",
        timeline_event_ids=[1, 2]
    )
    assert obs.evidence_id == "ev-123"

    hyp = MultiAgentHypothesis(
        id="H1",
        hypothesis="Memory leak",
        reasoning="Usage grew steadily",
        supporting_evidence=[],
        contradicting_evidence=[],
        missing_evidence=["heap dump"],
        immediate_mitigations=["Restart service"],
        preventative_measures=["Fix memory leak"]
    )
    assert hyp.id == "H1"

    val = ValidationFinding(
        hypothesis_id="H1",
        is_valid=True,
        contradicting_evidence=[],
        uncertainty_rationale="Looks good"
    )
    assert val.hypothesis_id == "H1"

    rank = RankedHypothesis(
        hypothesis_id="H1",
        rank=1,
        confidence_rationale="Most likely based on CPU"
    )
    assert rank.rank == 1

    rec = RecommendationResult(
        immediate_mitigations=["Restart service"],
        preventative_measures=["Fix memory leak"]
    )
    assert rec.immediate_mitigations == ["Restart service"]


def test_invalid_evidence_reference_structure():
    """Verify evidence requires valid structure."""
    with pytest.raises(ValidationError) as exc:
        MultiAgentHypothesis(
            id="H1",
            hypothesis="Test",
            reasoning="Test",
            supporting_evidence=[
                {"invalid_field": "bad"} # Missing evidence_id, filename, explanation
            ],
            contradicting_evidence=[],
            missing_evidence=[],
            immediate_mitigations=["Restart service"],
            preventative_measures=["Fix memory leak"]
        )
    assert "evidence_id" in str(exc.value)


def test_invalid_hypothesis_reference():
    """Verify ValidationFinding explicitly requires hypothesis_id."""
    with pytest.raises(ValidationError) as exc:
        ValidationFinding(
            is_valid=False,
            contradicting_evidence=[],
            uncertainty_rationale="Missing hyp id"
        )
    assert "hypothesis_id" in str(exc.value)


def test_invalid_ranking_reference():
    """Verify RankedHypothesis explicitly requires hypothesis_id and rank."""
    with pytest.raises(ValidationError) as exc:
        RankedHypothesis(
            rank=1,
            confidence_rationale="Missing hyp id"
        )
    assert "hypothesis_id" in str(exc.value)


def test_malformed_required_fields():
    """Verify missing required string fields throw ValidationError."""
    with pytest.raises(ValidationError) as exc:
        Observation(
            evidence_id="ev-123",
            timeline_event_ids=[1]
        ) # Missing description
    assert "description" in str(exc.value)


def test_empty_optional_collections():
    """Verify models safely handle empty collections."""
    # Recommendation Result with empty lists
    rec = RecommendationResult(
        immediate_mitigations=[],
        preventative_measures=[]
    )
    assert rec.immediate_mitigations == []
    assert rec.preventative_measures == []
