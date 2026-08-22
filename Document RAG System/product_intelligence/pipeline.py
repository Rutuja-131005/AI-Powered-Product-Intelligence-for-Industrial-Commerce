"""
Batch Processing Pipeline and Job Manager
Coordinates end-to-end enrichment for sparse input datasets with real-time status and telemetry.
"""

import asyncio
import io
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional
import pandas as pd

from .schema import EXPECTED_OUTPUT_COLUMNS, INPUT_COLUMNS
from .identity import resolve_brand, canonicalize_part_number
from .retriever import retrieve_rag_evidence, discover_authoritative_sources
from .extractor import extract_product_attributes
from .generator import generate_commerce_copy
from .validator import validate_and_score_product

class ProductIntelligencePipeline:
    """
    Manages batch catalog enrichment jobs, caching, and real-time state.
    """
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def enrich_single_product(self, row: Dict[str, Any], row_idx: int = 0) -> Dict[str, Any]:
        """
        Enriches a single sparse input product record into the full 252-column schema.
        Preserves all 6 input columns 100% verbatim.
        """
        # 1. Preserve original input values verbatim
        mfg_part_num = str(row.get("Mfg_Part_Num", "")).strip()
        if mfg_part_num.lower() in ["nan", "none", "null"]:
            mfg_part_num = ""
            
        part_desc = str(row.get("Part_Desc", "")).strip()
        if part_desc.lower() in ["nan", "none", "null"]:
            part_desc = ""

        e1_brand = str(row.get("E1_Brand", "")).strip()
        if e1_brand.lower() in ["nan", "none", "null"]:
            e1_brand = ""

        unilog_brand = str(row.get("Unilog_Brand", "")).strip()
        if unilog_brand.lower() in ["nan", "none", "null"]:
            unilog_brand = ""

        dib_brand = str(row.get("DIB_Brand", "")).strip()
        if dib_brand.lower() in ["nan", "none", "null"]:
            dib_brand = ""

        part_manuf = str(row.get("Part_Manuf", "")).strip()
        if part_manuf.lower() in ["nan", "none", "null"]:
            part_manuf = ""

        # 2. Identity Resolution
        resolved_brand, brand_conf = resolve_brand(
            e1_brand=e1_brand,
            unilog_brand=unilog_brand,
            dib_brand=dib_brand,
            part_manuf=part_manuf,
            part_desc=part_desc
        )
        canonical_pn, normalized_pn = canonicalize_part_number(mfg_part_num)

        # 3. Evidence Retrieval & Source Discovery
        rag_evidence = retrieve_rag_evidence(canonical_pn, resolved_brand, part_desc)
        sources_dict = discover_authoritative_sources(resolved_brand, canonical_pn)

        # 4. Structured Extraction & 50 Attribute Triplets
        specs = extract_product_attributes(canonical_pn, resolved_brand, part_desc, rag_evidence)
        triplets = specs.pop("triplets", {})

        # 5. Grounded Copy & SEO Generation
        commerce_copy = generate_commerce_copy(
            brand=resolved_brand,
            part_number=canonical_pn,
            part_desc=part_desc,
            specs=specs,
            rag_evidence=rag_evidence
        )

        # 6. Validation, Confidence & Provenance
        quality_metadata = validate_and_score_product(
            input_data=row,
            brand=resolved_brand,
            brand_confidence=brand_conf,
            part_number=canonical_pn,
            specs=specs,
            commerce_copy=commerce_copy,
            rag_evidence=rag_evidence,
            sources_dict=sources_dict
        )

        # 7. Assemble Complete Record adhering strictly to EXPECTED_OUTPUT_COLUMNS
        record: Dict[str, Any] = {}
        
        # Original 6
        record["Mfg_Part_Num"] = mfg_part_num
        record["Part_Desc"] = part_desc
        record["E1_Brand"] = e1_brand
        record["Unilog_Brand"] = unilog_brand
        record["DIB_Brand"] = dib_brand
        record["Part_Manuf"] = part_manuf

        # Identity
        record["Resolved_Brand"] = resolved_brand
        record["Canonical_Part_Number"] = canonical_pn
        record["Normalized_Part_Number"] = normalized_pn

        # Merge specs, commerce copy, sources, quality metadata
        for k, v in specs.items():
            if k in EXPECTED_OUTPUT_COLUMNS:
                record[k] = v

        for k, v in commerce_copy.items():
            if k in EXPECTED_OUTPUT_COLUMNS:
                record[k] = v

        for k, v in sources_dict.items():
            if k in EXPECTED_OUTPUT_COLUMNS:
                record[k] = v

        for k, v in quality_metadata.items():
            if k in EXPECTED_OUTPUT_COLUMNS:
                record[k] = v

        # Add all 50 Attribute Triplets
        for k, v in triplets.items():
            record[k] = v

        # Strict contract: ensure every expected column exists and is non-None
        final_record: Dict[str, Any] = {}
        for col in EXPECTED_OUTPUT_COLUMNS:
            final_record[col] = record.get(col, "")
            if final_record[col] is None:
                final_record[col] = ""

        # Attach helper metadata for frontend inspection
        final_record["_row_idx"] = row_idx
        final_record["_rag_evidence"] = rag_evidence

        return final_record

    def create_job(self, df: pd.DataFrame, filename: str = "upload.csv") -> str:
        """Initializes a new background enrichment job."""
        job_id = str(uuid.uuid4())[:8]
        self.jobs[job_id] = {
            "job_id": job_id,
            "filename": filename,
            "status": "QUEUED",
            "total_rows": len(df),
            "processed_rows": 0,
            "failed_rows": 0,
            "progress_percent": 0.0,
            "start_time": time.time(),
            "end_time": None,
            "records": [],
            "raw_dataframe": df
        }
        return job_id

    async def run_batch_job(self, job_id: str, batch_size: int = 25):
        """Asynchronously executes batch enrichment for the job."""
        job = self.jobs.get(job_id)
        if not job:
            return

        job["status"] = "RUNNING"
        df = job["raw_dataframe"]
        total = len(df)
        records = []

        try:
            for idx, row in df.iterrows():
                if job.get("status") == "CANCELLED":
                    break
                    
                row_dict = row.to_dict()
                try:
                    enriched = self.enrich_single_product(row_dict, row_idx=idx)
                    records.append(enriched)
                except Exception as e:
                    job["failed_rows"] += 1
                    # Graceful degradation: build default record with raw data
                    fallback = {col: str(row_dict.get(col, "")) for col in EXPECTED_OUTPUT_COLUMNS}
                    fallback["_row_idx"] = idx
                    fallback["Validation_Status"] = "FAILED"
                    fallback["Review_Status"] = "NEEDS_REVIEW"
                    fallback["Overall_Confidence_Score"] = "0.10"
                    fallback["_rag_evidence"] = []
                    records.append(fallback)

                job["processed_rows"] = len(records)
                job["progress_percent"] = round((len(records) / max(1, total)) * 100, 1)

                # Yield control to event loop periodically
                if idx % batch_size == 0:
                    await asyncio.sleep(0.01)

            job["records"] = records
            job["status"] = "COMPLETED" if job.get("status") != "CANCELLED" else "CANCELLED"
            job["end_time"] = time.time()

        except Exception as e:
            job["status"] = "FAILED"
            job["error"] = str(e)
            job["end_time"] = time.time()

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        elapsed = round(time.time() - job["start_time"], 1) if job["status"] == "RUNNING" else round((job["end_time"] or time.time()) - job["start_time"], 1)
        
        # Calculate summary KPIs
        records = job.get("records", [])
        avg_confidence = 0.0
        verified_count = 0
        needs_review_count = 0
        
        if records:
            scores = []
            for r in records:
                try:
                    scores.append(float(r.get("Overall_Confidence_Score", 0.0)))
                except:
                    pass
                if r.get("Validation_Status") == "VERIFIED":
                    verified_count += 1
                elif r.get("Validation_Status") in ["NEEDS_REVIEW", "FAILED"]:
                    needs_review_count += 1
            if scores:
                avg_confidence = round(sum(scores) / len(scores), 2)

        return {
            "job_id": job["job_id"],
            "filename": job["filename"],
            "status": job["status"],
            "total_rows": job["total_rows"],
            "processed_rows": job["processed_rows"],
            "failed_rows": job["failed_rows"],
            "progress_percent": job["progress_percent"],
            "elapsed_seconds": elapsed,
            "avg_confidence": avg_confidence,
            "verified_count": verified_count,
            "needs_review_count": needs_review_count
        }

    def get_job_products(
        self,
        job_id: str,
        page: int = 1,
        page_size: int = 20,
        search_query: str = "",
        brand_filter: str = "",
        status_filter: str = ""
    ) -> Dict[str, Any]:
        """Retrieves paginated and filtered product records for the UI table."""
        job = self.jobs.get(job_id)
        if not job:
            return {"total": 0, "page": page, "page_size": page_size, "products": []}

        records = job.get("records", [])
        filtered = records

        # Filter by search
        if search_query:
            q = search_query.lower()
            filtered = [
                r for r in filtered
                if q in str(r.get("Mfg_Part_Num", "")).lower()
                or q in str(r.get("Part_Desc", "")).lower()
                or q in str(r.get("Resolved_Brand", "")).lower()
                or q in str(r.get("Product_Title", "")).lower()
            ]

        # Filter by brand
        if brand_filter and brand_filter != "ALL":
            filtered = [r for r in filtered if r.get("Resolved_Brand") == brand_filter]

        # Filter by validation status
        if status_filter and status_filter != "ALL":
            filtered = [r for r in filtered if r.get("Validation_Status") == status_filter]

        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        page_records = filtered[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "products": page_records
        }

    def update_product_field(self, job_id: str, row_idx: int, field_name: str, new_value: str) -> bool:
        """Allows technical reviewer to update or approve a field."""
        job = self.jobs.get(job_id)
        if not job:
            return False
        records = job.get("records", [])
        if 0 <= row_idx < len(records):
            records[row_idx][field_name] = new_value
            records[row_idx]["Review_Status"] = "EDITED"
            return True
        return False

# Global singleton
_pipeline_instance = None

def get_pipeline_instance() -> ProductIntelligencePipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ProductIntelligencePipeline()
    return _pipeline_instance
