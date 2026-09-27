"""
Evidence Engine Skeleton
------------------------
Responsible for aggregating evidence for AI reasoning.
It attaches source, valid-time, and confidence metadata to every datum.
"""

from datetime import datetime, timezone

def format_evidence(source: str, parameter: str, value: any, confidence: float, valid_time: str) -> dict:
    """Format a single piece of evidence per the ORCA Standard Data Model."""
    return {
        "source": source,
        "parameter": parameter,
        "value": value,
        "confidence": confidence,
        "valid_time": valid_time,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "is_stale": False,
        "conflict_flag": False
    }

def aggregate_evidence(data_points: list) -> dict:
    """Aggregates multiple evidence points to pass to the Synthesizer."""
    return {
        "aggregated_evidence": data_points,
        "total_sources_used": len(set([d.get("source") for d in data_points])),
        "overall_confidence": sum([d.get("confidence", 0) for d in data_points]) / max(len(data_points), 1)
    }
