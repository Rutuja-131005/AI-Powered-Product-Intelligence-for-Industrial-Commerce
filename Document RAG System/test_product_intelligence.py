"""
Unit and Integration Tests for AI-Powered Product Intelligence Engine
Verifies Schema Compliance, Preservation of Input, 50 Triplets, and Export.
"""

import sys
import os
import io
import pandas as pd
import asyncio

# Ensure Document RAG System is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from product_intelligence.schema import EXPECTED_OUTPUT_COLUMNS, NUM_OUTPUT_COLUMNS, INPUT_COLUMNS
from product_intelligence.identity import resolve_brand, canonicalize_part_number
from product_intelligence.pipeline import get_pipeline_instance
from product_intelligence.exporter import export_to_csv_bytes, export_to_xlsx_bytes

def test_schema_column_count():
    print("Test 1: Schema Column Count Contract...")
    assert len(EXPECTED_OUTPUT_COLUMNS) == 252, f"Expected 252 columns, got {len(EXPECTED_OUTPUT_COLUMNS)}"
    assert len(EXPECTED_OUTPUT_COLUMNS) == NUM_OUTPUT_COLUMNS
    print(f"  [PASS] Exact 252 columns verified.")

def test_input_columns_preservation():
    print("Test 2: Input Columns Preservation...")
    for col in INPUT_COLUMNS:
        assert col in EXPECTED_OUTPUT_COLUMNS[:6], f"Input column {col} not in first 6 headers"
    print("  [PASS] All 6 original input columns present in initial positions.")

def test_identity_resolution():
    print("Test 3: Identity & Brand Resolution...")
    brand, conf = resolve_brand(
        e1_brand="ALLEN BRADLEY",
        unilog_brand="Allen-Bradley",
        dib_brand="ROCKWELL",
        part_manuf="Rockwell Automation"
    )
    assert brand == "Allen-Bradley", f"Expected Allen-Bradley, got {brand}"
    assert conf >= 0.80, f"Expected high confidence, got {conf}"

    canon_pn, norm_pn = canonicalize_part_number("140U-J0D3-C40")
    assert canon_pn == "140U-J0D3-C40"
    assert norm_pn == "140UJ0D3C40"
    print(f"  [PASS] Brand resolved: {brand} (Confidence: {conf}), Canon PN: {canon_pn}")

def test_single_product_enrichment():
    print("Test 4: Single Product Enrichment & 50 Triplets...")
    pipeline = get_pipeline_instance()
    
    sample_input = {
        "Mfg_Part_Num": "140U-J0D3-C40",
        "Part_Desc": "CIR BRKR 40A 3P 600V MOLDED CASE",
        "E1_Brand": "ALLEN BRADLEY",
        "Unilog_Brand": "Allen-Bradley",
        "DIB_Brand": "ROCKWELL",
        "Part_Manuf": "Rockwell Automation"
    }
    
    enriched = pipeline.enrich_single_product(sample_input)
    
    # 1. Verify all 252 columns present
    for col in EXPECTED_OUTPUT_COLUMNS:
        assert col in enriched, f"Missing expected column {col}"
        
    # 2. Verify 100% preservation of raw input
    assert enriched["Mfg_Part_Num"] == sample_input["Mfg_Part_Num"]
    assert enriched["Part_Desc"] == sample_input["Part_Desc"]
    assert enriched["E1_Brand"] == sample_input["E1_Brand"]
    assert enriched["Unilog_Brand"] == sample_input["Unilog_Brand"]
    assert enriched["DIB_Brand"] == sample_input["DIB_Brand"]
    assert enriched["Part_Manuf"] == sample_input["Part_Manuf"]

    # 3. Verify extracted technical specs
    assert enriched["Resolved_Brand"] == "Allen-Bradley"
    assert enriched["Primary_Category"] == "Electrical Distribution & Protection"
    assert enriched["Current_Rating"] == "40"
    assert enriched["Attribute_Value_3"] == "3"

    # 4. Verify 10 feature bullets
    for i in range(1, 11):
        assert f"Feature_Bullet_{i}" in enriched
        assert len(enriched[f"Feature_Bullet_{i}"]) > 0

    # 5. Verify 50 attribute triplets
    for i in range(1, 51):
        assert f"Attribute_Name_{i}" in enriched
        assert f"Attribute_Value_{i}" in enriched
        assert f"Attribute_UOM_{i}" in enriched

    # 6. Verify validation & confidence score
    assert float(enriched["Overall_Confidence_Score"]) >= 0.70
    assert enriched["Validation_Status"] in ["VERIFIED", "PARTIAL"]
    print(f"  [PASS] Enriched product title: '{enriched['Product_Title']}' (Confidence: {enriched['Overall_Confidence_Score']})")

def test_batch_pipeline_and_export():
    print("Test 5: Batch Processing & 252-Col CSV / XLSX Export...")
    pipeline = get_pipeline_instance()
    
    sample_df = pd.DataFrame([
        {
            "Mfg_Part_Num": "140U-J0D3-C40",
            "Part_Desc": "CIR BRKR 40A 3P 600V MOLDED CASE",
            "E1_Brand": "ALLEN BRADLEY",
            "Unilog_Brand": "Allen-Bradley",
            "DIB_Brand": "ROCKWELL",
            "Part_Manuf": "Rockwell Automation"
        },
        {
            "Mfg_Part_Num": "LC1D25BD",
            "Part_Desc": "CONTACTOR 25A 24VDC 3P TEESYS D",
            "E1_Brand": "SQUARE D",
            "Unilog_Brand": "Schneider Electric",
            "DIB_Brand": "SQUARED",
            "Part_Manuf": "Schneider Electric"
        },
        {
            "Mfg_Part_Num": "3RV2011-1AA10",
            "Part_Desc": "CIR BRKR SIZE S00 MOTOR PROT 0.9-1.25A",
            "E1_Brand": "SIEMENS",
            "Unilog_Brand": "Siemens AG",
            "DIB_Brand": "SIEMENS",
            "Part_Manuf": "Siemens Industry"
        }
    ])
    
    job_id = pipeline.create_job(sample_df, filename="test_batch.csv")
    asyncio.run(pipeline.run_batch_job(job_id))
    
    status = pipeline.get_job_status(job_id)
    assert status["status"] == "COMPLETED"
    assert status["processed_rows"] == 3
    assert status["failed_rows"] == 0
    
    job = pipeline.jobs[job_id]
    records = job["records"]
    assert len(records) == 3
    
    # Export CSV
    csv_bytes = export_to_csv_bytes(records)
    exported_df = pd.read_csv(io.BytesIO(csv_bytes))
    assert list(exported_df.columns) == EXPECTED_OUTPUT_COLUMNS
    assert len(exported_df) == 3
    
    # Export XLSX
    xlsx_bytes = export_to_xlsx_bytes(records)
    xlsx_df = pd.read_excel(io.BytesIO(xlsx_bytes))
    assert list(xlsx_df.columns) == EXPECTED_OUTPUT_COLUMNS
    assert len(xlsx_df) == 3
    
    print("  [PASS] CSV & XLSX generated with exactly 252 matching columns and 3 preserved rows.")

if __name__ == "__main__":
    test_schema_column_count()
    test_input_columns_preservation()
    test_identity_resolution()
    test_single_product_enrichment()
    test_batch_pipeline_and_export()
    print("\n=======================================================")
    print("ALL AI PRODUCT INTELLIGENCE PIPELINE TESTS PASSED (100%)")
    print("=======================================================")
