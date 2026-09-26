import re
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel

class TimelineEvent(BaseModel):
    timestamp: datetime
    evidence_id: str
    filename: str
    content: str
    line_number: int

# Matches:
# 2026-09-10 18:20:01
# 2026-09-10T18:20:01Z
# 2026-09-10T18:20:01+00:00
# 2026-09-10 18:20:01.123
TIMESTAMP_REGEX = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
)

def _parse_timestamp(ts_str: str) -> datetime:
    """Safely parse matched timestamp strings into timezone-aware datetimes."""
    # Normalize separator
    ts_str = ts_str.replace(" ", "T")
    
    # Handle 'Z' suffix natively missing in older pythons or strict isoformat
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1] + "+00:00"
        
    dt = datetime.fromisoformat(ts_str)
    
    # If naive (no timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    return dt

def extract_timeline(evidence_files: list[tuple[str, str, str]]) -> list[TimelineEvent]:
    """
    Extracts chronological events from raw text evidence.
    
    Args:
        evidence_files: A list of tuples containing (evidence_id, filename, file_content)
        
    Returns:
        A chronologically sorted list of TimelineEvent objects.
    """
    events = []
    
    for evidence_id, filename, content in evidence_files:
        if not content:
            continue
            
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            match = TIMESTAMP_REGEX.search(line)
            if match:
                try:
                    dt = _parse_timestamp(match.group("ts"))
                    events.append(TimelineEvent(
                        timestamp=dt,
                        evidence_id=str(evidence_id),
                        filename=filename,
                        content=line,  # Preserve the entire original evidence text
                        line_number=idx + 1
                    ))
                except ValueError:
                    # Safely skip malformed timestamps that passed the initial regex
                    pass
                    
    # Sort chronologically.
    # Python's list.sort() is guaranteed to be stable,
    # so identical timestamps preserve their original line order.
    events.sort(key=lambda e: e.timestamp)
    
    return events
