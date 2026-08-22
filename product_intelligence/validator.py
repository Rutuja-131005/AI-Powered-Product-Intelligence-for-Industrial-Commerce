"""
Validation, Provenance Tracking, and Confidence Engine
Evaluates factual grounding, calculates confidence scores, and builds provenance audit logs.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

def validate_and_score_product(
    input_data: Dict[str, Any],
    brand: str,
    brand_confidence: float,
    part_number: str,
    specs: Dict[str, Any],
    commerce_copy: Dict[str, Any],
    rag_evidence: List[Dict[str, Any]],
    sources_dict: Dict[str, str]
) -> Dict[str, Any]:
    """
    Computes overall confidence score, provenance log, validation status,
    and review status for the enriched product record.
    """
    field_scores: Dict[str, float] = {}
    provenance_entries: List[Dict[str, Any]] = []

    # 1. Brand & Identity Provenance
    field_scores["Resolved_Brand"] = brand_confidence
    provenance_entries.append({
        "field": "Resolved_Brand",
        "value": brand,
        "source": "Multi-Brand Consensus & Alias Mapping",
        "confidence": brand_confidence
    })

    # 2. Canonical Part Number Provenance
    field_scores["Canonical_Part_Number"] = 1.0
    provenance_entries.append({
        "field": "Canonical_Part_Number",
        "value": part_number,
        "source": "Source Input Mfg_Part_Num",
        "confidence": 1.0
    })

    # 3. Evidence grounding factor
    has_rag_doc = len(rag_evidence) > 0
    rag_boost = 0.15 if has_rag_doc else 0.0
    
    if has_rag_doc:
        top_rag = rag_evidence[0]
        provenance_entries.append({
            "field": "Technical_Specifications",
            "source": f"ChromaDB Vector Match: {top_rag['source_title']}",
            "snippet": top_rag['content_snippet'][:150],
            "confidence": top_rag['confidence_score']
        })

    # 4. Specifications Provenance
    spec_conf = min(0.98, max(0.70, 0.78 + rag_boost))
    field_scores["Taxonomy"] = spec_conf
    field_scores["Product_Title"] = spec_conf
    field_scores["Short_Description"] = spec_conf
    field_scores["Electrical_Mechanical_Specs"] = spec_conf

    for key in ["Voltage_Rating", "Current_Rating", "Mounting_Type", "Product_Type"]:
        if specs.get(key):
            provenance_entries.append({
                "field": key,
                "value": str(specs[key]),
                "source": "Descriptor Regex & Domain Rules Engine",
                "confidence": spec_conf
            })

    # 5. External Discovered Sources
    provenance_entries.append({
        "field": "Manufacturer_Product_URL",
        "value": sources_dict.get("Manufacturer_Product_URL", ""),
        "source": f"Authoritative Manufacturer Portal ({brand})",
        "confidence": 0.95
    })

    # 6. Overall Confidence Calculation (weighted mean)
    overall_confidence = round(
        (brand_confidence * 0.25) +
        (1.0 * 0.20) +
        (spec_conf * 0.40) +
        (0.95 * 0.15),
        2
    )

    # 7. Determine Validation Status
    if overall_confidence >= 0.85:
        val_status = "VERIFIED"
    elif overall_confidence >= 0.70:
        val_status = "PARTIAL"
    else:
        val_status = "NEEDS_REVIEW"

    # Evidence sources count (RAG docs + external authoritative URLs)
    evidence_count = len(rag_evidence) + len([url for url in sources_dict.values() if url])

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "Overall_Confidence_Score": str(overall_confidence),
        "Validation_Status": val_status,
        "Review_Status": "PENDING",
        "Evidence_Sources_Count": str(evidence_count),
        "Provenance_Log": json.dumps(provenance_entries),
        "Enrichment_Method": "AI-RAG-Hybrid-Enricher-v2.0",
        "Last_Enriched_Timestamp": now_iso
    }
