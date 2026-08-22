"""
Confidence Scoring Engine
Calculates score and classifies tier:
- 0.95–1.00: Exact manufacturer evidence
- 0.85–0.94: Strong official/reference evidence
- 0.70–0.84: Reliable secondary source
- 0.50–0.69: Inferred/weak evidence
- <0.50: Unsupported; blank or review
"""

from typing import Dict, Any, Tuple

def compute_confidence_score(
    identity_conf: float,
    has_rag_evidence: bool,
    has_spec_extracted: bool,
    source_weight: float = 0.90
) -> Tuple[float, str]:
    rag_boost = 0.15 if has_rag_evidence else 0.0
    spec_score = 0.85 if has_spec_extracted else 0.65
    
    score = round(
        (identity_conf * 0.30) +
        (spec_score * 0.35) +
        (source_weight * 0.20) +
        (rag_boost * 0.15),
        2
    )
    score = min(1.0, max(0.10, score))

    if score >= 0.95:
        tier = "EXACT_MANUFACTURER_EVIDENCE"
    elif score >= 0.85:
        tier = "STRONG_OFFICIAL_EVIDENCE"
    elif score >= 0.70:
        tier = "RELIABLE_SECONDARY_SOURCE"
    elif score >= 0.50:
        tier = "INFERRED_EVIDENCE"
    else:
        tier = "NEEDS_REVIEW"

    return score, tier
