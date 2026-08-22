"""
Services — Product Intelligence Pipeline
Orchestrates end-to-end processing from sparse inputs into 252-column schema,
database persistence, and Google Spreadsheet synchronization.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from product.identity import resolve_product_identity
from product.extractor import extract_specifications
from product.normalizer import normalize_uom
from product.validator import validate_product_record
from product.confidence import compute_confidence_score
from product.enricher import enrich_product_copy
from sources.search import search_sources
from sources.source_ranker import rank_sources
from export.mapper import map_record_to_252_columns
from export.output_schema import FINAL_252_HEADERS
from db.sheets_sync import GoogleSheetsSync

class ProductPipeline:
    """Master pipeline orchestrator for product intelligence."""

    @classmethod
    def process_single_row(cls, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        """Processes a single raw product record through the full 252-column enrichment lifecycle."""
        # 1. Identity Resolution
        ident = resolve_product_identity(
            mfg_part_num=raw_row.get("Mfg_Part_Num", ""),
            part_desc=raw_row.get("Part_Desc", ""),
            e1_brand=raw_row.get("E1_Brand", ""),
            unilog_brand=raw_row.get("Unilog_Brand", ""),
            dib_brand=raw_row.get("DIB_Brand", ""),
            part_manuf=raw_row.get("Part_Manuf", "")
        )
        brand = ident["Resolved_Brand"]
        part_num = ident["Canonical_Part_Number"]

        # 2. Multi-Website Source Discovery & Ranking
        sources = search_sources(brand, part_num)
        ranked = rank_sources(sources)

        # 3. Technical Specification Extraction & Copy Generation
        specs = extract_specifications(raw_row.get("Part_Desc", ""), part_num)
        copy_data = enrich_product_copy(brand, part_num, raw_row.get("Part_Desc", ""), specs)

        # 4. Confidence & Validation Scoring
        conf_score, conf_tier = compute_confidence_score(ident, specs, sources)
        val_status = "VERIFIED" if conf_score >= 0.85 else "PARTIAL"

        enriched_payload = {
            **ident,
            **specs,
            **copy_data,
            **sources,
            "BRAND_NAME": brand,
            "MANUFACTURER": raw_row.get("Part_Manuf", f"{brand} Corporation"),
            "PRIMARY_CATEGORY": "Industrial Tools & Electrical Hardware",
            "Validation_Status": val_status,
            "Overall_Confidence_Score": f"{conf_score:.2f}",
            "Review_Status": "APPROVED" if val_status == "VERIFIED" else "PENDING"
        }

        # 5. Exact 252-Column Contractual Mapping
        mapped_252 = map_record_to_252_columns(enriched_payload, raw_row)

        # 6. Synchronize to Google Sheets Database Sink
        sheets_res = GoogleSheetsSync.sync_record(mapped_252)
        mapped_252["_sheets_sync"] = sheets_res

        return mapped_252

    @classmethod
    def process_batch(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Processes a pandas DataFrame of raw product rows."""
        results = []
        for _, row in df.iterrows():
            processed = cls.process_single_row(row.to_dict())
            results.append(processed)
        return results

_pipeline_instance = ProductPipeline()

def get_product_pipeline() -> ProductPipeline:
    return _pipeline_instance
