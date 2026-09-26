import json

# Valid scenario: all fields perfectly formed, evidence matches.
SCENARIO_A_VALID = {
    "summary": "Database connection pool exhausted.",
    "root_cause": "H1",
    "recommendations": "Increase pool size.",
    "supporting_evidence": [
        {"evidence_id": "ev-1", "filename": "db.log", "explanation": "Shows connection timeouts."}
    ],
    "contradicting_evidence": [],
    "missing_evidence": [],
    "hypotheses": [
        {
            "id": "H1",
            "hypothesis": "Pool exhausted.",
            "reasoning": "Logs indicate timeout.",
            "supporting_evidence": [
                {"evidence_id": "ev-1", "filename": "db.log", "explanation": "Shows timeouts."}
            ],
            "contradicting_evidence": [],
            "missing_evidence": []
        }
    ]
}

# Invalid scenario: references evidence ID that wasn't supplied
SCENARIO_B_INVALID_EVIDENCE_ID = {
    "summary": "Database connection pool exhausted.",
    "root_cause": "H1",
    "recommendations": "Increase pool size.",
    "supporting_evidence": [
        {"evidence_id": "ev-fake-999", "filename": "db.log", "explanation": "This ID does not exist in the incident."}
    ],
    "contradicting_evidence": [],
    "missing_evidence": [],
    "hypotheses": [
        {
            "id": "H1",
            "hypothesis": "Pool exhausted.",
            "reasoning": "Logs indicate timeout.",
            "supporting_evidence": [
                {"evidence_id": "ev-fake-999", "filename": "db.log", "explanation": "Shows timeouts."}
            ],
            "contradicting_evidence": [],
            "missing_evidence": []
        }
    ]
}

# Missing fields scenario (malformed LLM output)
SCENARIO_C_MALFORMED = {
    "summary": "It broke.",
    # Missing root_cause
    "recommendations": "Fix it.",
    "supporting_evidence": [],
    "contradicting_evidence": [],
    "missing_evidence": [],
    "hypotheses": []
}

# Scenario with missing evidence stated correctly
SCENARIO_D_MISSING_INFO = {
    "summary": "Deployment failed.",
    "root_cause": "H2",
    "recommendations": "Rollback.",
    "supporting_evidence": [],
    "contradicting_evidence": [],
    "missing_evidence": ["Need application logs to confirm.", "Missing APM traces."],
    "hypotheses": [
        {
            "id": "H2",
            "hypothesis": "Bad config deployed.",
            "reasoning": "Timing aligns with deploy, but we lack logs.",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "missing_evidence": ["Need application logs to confirm."]
        }
    ]
}

SUPPLIED_EVIDENCE_POOL = {"ev-1", "ev-2"}
