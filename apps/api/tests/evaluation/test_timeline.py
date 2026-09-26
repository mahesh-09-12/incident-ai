import pytest
from datetime import datetime, timezone
from app.features.investigation.timeline import extract_timeline

def test_single_log_multiple_timestamps():
    content = """
    2026-09-10 18:20:05 Error occurred
    2026-09-10 18:20:01 Booting system
    """
    evidence = [("ev-1", "app.log", content)]
    timeline = extract_timeline(evidence)
    
    assert len(timeline) == 2
    # Ensure chronological order
    assert timeline[0].content.strip() == "2026-09-10 18:20:01 Booting system"
    assert timeline[1].content.strip() == "2026-09-10 18:20:05 Error occurred"
    assert timeline[0].line_number == 3
    assert timeline[1].line_number == 2

def test_multiple_evidence_files_and_ids_preserved():
    content1 = "2026-09-10T18:20:02Z Database connect"
    content2 = "2026-09-10T18:20:01Z Web server start"
    
    evidence = [
        ("ev-db", "db.log", content1),
        ("ev-web", "web.log", content2)
    ]
    
    timeline = extract_timeline(evidence)
    assert len(timeline) == 2
    
    # Chronological sort across files
    assert timeline[0].content == content2
    assert timeline[0].evidence_id == "ev-web"
    assert timeline[0].filename == "web.log"
    
    assert timeline[1].content == content1
    assert timeline[1].evidence_id == "ev-db"
    assert timeline[1].filename == "db.log"

def test_iso8601_timestamps():
    content = "2026-09-10T18:20:01+05:00 Timezone test"
    evidence = [("ev-1", "test.log", content)]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 1
    assert timeline[0].timestamp.tzinfo is not None

def test_millisecond_timestamps():
    content = "2026-09-10 18:20:01.123 Millisecond test"
    evidence = [("ev-1", "test.log", content)]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 1
    assert timeline[0].timestamp.microsecond == 123000

def test_lines_without_timestamps():
    content = """
    2026-09-10 18:20:01 First
    This line has no timestamp
    And neither does this one
    2026-09-10 18:20:05 Second
    """
    evidence = [("ev-1", "test.log", content)]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 2
    assert "First" in timeline[0].content
    assert "Second" in timeline[1].content

def test_malformed_timestamps():
    # Looks like a timestamp but fails datetime parsing (month 13, invalid)
    content = "2026-13-10 18:20:01 Malformed"
    evidence = [("ev-1", "test.log", content)]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 0

def test_empty_evidence():
    evidence = [
        ("ev-1", "empty.log", ""),
        ("ev-2", "none.log", None),  # Simulate null content safely skipped
    ]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 0

def test_identical_timestamps_preserve_order():
    content = """
    2026-09-10 18:20:01 Event A
    2026-09-10 18:20:01 Event B
    """
    evidence = [("ev-1", "test.log", content)]
    timeline = extract_timeline(evidence)
    assert len(timeline) == 2
    assert timeline[0].timestamp == timeline[1].timestamp
    # Python stable sort guarantees A comes before B as they appeared in that order
    assert "Event A" in timeline[0].content
    assert "Event B" in timeline[1].content
