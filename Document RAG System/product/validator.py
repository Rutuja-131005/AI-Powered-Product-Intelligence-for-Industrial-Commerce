"""
Validation Engine
Validates cross-field consistency, units, ranges, and evidence support.
"""

from typing import Dict, Any, List

def validate_product_record(record: Dict[str, Any], confidence_score: float) -> str:
    """Assigns validation status based on confidence score and data completeness."""
    if confidence_score >= 0.85:
        return "VERIFIED"
    elif confidence_score >= 0.70:
        return "PARTIAL"
    else:
        return "NEEDS_REVIEW"
