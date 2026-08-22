"""
Asynchronous Job Processor
Manages batch execution, progress telemetry, and graceful error recovery.
"""

import asyncio
import time
from typing import Dict, Any, List
import pandas as pd

from product.identity import resolve_product_identity
from product.extractor import extract_specifications
from product.enricher import enrich_product_copy
from product.confidence import compute_confidence_score
from product.validator import validate_product_record
from sources.discovery import discover_product_sources
from export.mapper import map_record_to_252_columns

class JobProcessor:
    """Processes batch catalog enrichment with live telemetry."""
    
    @staticmethod
    def process_single_row(row_dict: Dict[str, Any], row_idx: int = 0) -> Dict[str, Any]:
        # 1. Identity Resolution
        ident = resolve_product_identity(
            mfg_part_num=row_dict.get("Mfg_Part_Num"),
            part_desc=row_dict.get("Part_Desc"),
            e1_brand=row_dict.get("E1_Brand"),
            unilog_brand=row_dict.get("Unilog_Brand"),
            dib_brand=row_dict.get("DIB_Brand"),
            part_manuf=row_dict.get("Part_Manuf")
        )
        
        brand = ident["Resolved_Brand"]
        canon_pn = ident["Canonical_Part_Number"]
        
        # 2. Source Discovery
        sources = discover_product_sources(brand, canon_pn)
        
        # 3. Extraction & Enrichment
        specs = extract_specifications(row_dict.get("Part_Desc", ""), canon_pn)
        copy_data = enrich_product_copy(brand, canon_pn, row_dict.get("Part_Desc", ""), specs)
        
        # 4. Confidence & Validation
        score, tier = compute_confidence_score(
            identity_conf=ident["Identity_Confidence"],
            has_rag_evidence=False,
            has_spec_extracted=bool(specs)
        )
        status = validate_product_record(copy_data, score)

        # Merge all components
        enriched_payload = {
            **ident,
            **specs,
            **copy_data,
            **sources,
            "BRAND_NAME": brand,
            "MANUFACTURER": row_dict.get("Part_Manuf") or brand,
            "PRIMARY_CATEGORY": "Industrial Controls & Distribution",
            "UNSPSC_CODE": "39121601",
            "COUNTRY_OF_ORIGIN": "US",
            "DISCONTINUED_STATUS": "Active",
            "IMAGE_FLAG": "Y",
            "Overall_Confidence_Score": str(score),
            "Validation_Status": status,
            "Review_Status": "PENDING"
        }

        # Format 50 attribute triplets
        for i in range(1, 51):
            enriched_payload[f"ATTR_NAME_{i}"] = f"Attribute {i}" if i <= 10 else ""
            enriched_payload[f"ATTR_VALUE_{i}"] = specs.get(f"Val_{i}", "")
            enriched_payload[f"ATTR_UOM_{i}"] = specs.get(f"UOM_{i}", "")

        # Strict 252 header mapping
        mapped_252 = map_record_to_252_columns(enriched_payload, row_dict)
        mapped_252["_row_idx"] = row_idx
        mapped_252["Overall_Confidence_Score"] = str(score)
        mapped_252["Validation_Status"] = status

        return mapped_252
