"""
Source Ranking Hierarchy and Trust Evaluator
"""

from typing import Dict, Any

SOURCE_RANKING_TIERS = {
    "MANUFACTURER_EXACT": 1.00,
    "MANUFACTURER_SPEC_SHEET": 0.98,
    "MANUFACTURER_MANUAL": 0.95,
    "MANUFACTURER_CATALOG": 0.90,
    "AUTHORIZED_DISTRIBUTOR": 0.85,
    "TECHNICAL_REFERENCE": 0.75,
    "SEARCH_SNIPPET": 0.50
}

def evaluate_source_weight(source_type: str) -> float:
    return SOURCE_RANKING_TIERS.get(source_type.upper(), 0.70)
