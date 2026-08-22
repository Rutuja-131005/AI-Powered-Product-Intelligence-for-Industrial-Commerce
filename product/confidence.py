"""
Confidence Scoring Engine
Calculates score and classifies tier:
- 0.95–1.00: Exact manufacturer evidence
- 0.85–0.94: Strong official/reference evidence
- 0.70–0.84: Reliable secondary source
- 0.50–0.69: Inferred/weak evidence
- <0.50: Unsupported; blank or review
"""

from typing import Dict, Any, Tuple, Union

def compute_confidence_score(
    identity_conf: Union[float, Dict[str, Any]],
    has_rag_evidence: Union[bool, Dict[str, Any]] = True,
    has_spec_extracted: Union[bool, Dict[str, Any]] = True,
    source_weight: float = 0.90
) -> Tuple[float, str]:
    if isinstance(identity_conf, dict):
        id_val = float(identity_conf.get("Identity_Confidence_Score", 0.95))
    else:
        try:
            id_val = float(identity_conf)
        except (ValueError, TypeError):
            id_val = 0.95

    has_rag = bool(has_rag_evidence)
    has_specs = bool(has_spec_extracted)

    rag_boost = 0.15 if has_rag else 0.0
    spec_score = 0.85 if has_specs else 0.65

    score = round(
        (id_val * 0.30) +
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
