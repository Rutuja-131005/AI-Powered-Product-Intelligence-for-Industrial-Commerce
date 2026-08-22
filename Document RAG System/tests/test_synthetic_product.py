"""
Dynamic Evaluation Test: Synthetic Unseen Industrial Product
Tests dynamic generalization on a completely novel industrial part not in any sample set.
"""

import sys
import os
import io
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.processor import JobProcessor
from export.output_schema import FINAL_252_HEADERS
from export.exporter import export_catalog_to_csv, export_catalog_to_xlsx

def test_novel_synthetic_product_enrichment():
    """
    Tests dynamic extraction, identity resolution, commerce generation,
    and 252-column schema mapping on a novel synthetic Yokogawa / Mitsubishi part.
    """
    novel_input = {
        "Mfg_Part_Num": "EJA110E-JMS4G-917EB",
        "Part_Desc": "DIFF PRESSURE TRANSMITTER 0-100 KPA 4-20MA HART SIL2 FLANGE",
        "E1_Brand": "YOKOGAWA",
        "Unilog_Brand": "Yokogawa Electric",
        "DIB_Brand": "YOKOGAWA",
        "Part_Manuf": "Yokogawa Electric Corporation"
    }

    # Execute processing
    processed = JobProcessor.process_single_row(novel_input, 0)

    # 1. Verify preservation
    assert processed["Mfg_Part_Num"] == "EJA110E-JMS4G-917EB"
    assert processed["Part_Desc"] == novel_input["Part_Desc"]
    assert processed["E1_Brand"] == "YOKOGAWA"
    assert processed["Unilog_Brand"] == "Yokogawa Electric"
    assert processed["DIB_Brand"] == "YOKOGAWA"
    assert processed["Part_Manuf"] == "Yokogawa Electric Corporation"

    # 2. Verify dynamic brand resolution
    assert processed["BRAND_NAME"] == "Yokogawa Electric"
    assert processed["PART_NUMBER"] == "EJA110E-JMS4G-917EB"
    assert processed["MANUFACTURER_PART_NUMBER"] == "EJA110E-JMS4G-917EB"

    # 3. Verify extracted and enriched fields
    assert processed["_status"] == "COMPLETED"
    assert processed["_validation_status"] in ["VERIFIED", "PARTIAL"]
    assert len(processed["Product Name"]) > 0
    assert len(processed["SHORT_DESC"]) > 0
    assert len(processed["LONG_DESC1"]) > 0
    assert len(processed["ITEM_FEATURES_1"]) > 0

    # 4. Verify exact 252-column output contract
    csv_bytes = export_catalog_to_csv([processed])
    df_csv = pd.read_csv(io.BytesIO(csv_bytes))
    assert list(df_csv.columns) == FINAL_252_HEADERS
    assert len(df_csv) == 1

    xlsx_bytes = export_catalog_to_xlsx([processed])
    df_xlsx = pd.read_excel(io.BytesIO(xlsx_bytes))
    assert list(df_xlsx.columns) == FINAL_252_HEADERS
    assert len(df_xlsx) == 1

    print(f"[PASS] Novel synthetic product processed dynamically:")
    print(f"       Product: {processed['Product Name']}")
    print(f"       Brand: {processed['BRAND_NAME']}")
    print(f"       Status: {processed['_validation_status']}")
    print(f"       Export Schema: 252/252 Columns Validated.")

if __name__ == "__main__":
    test_novel_synthetic_product_enrichment()
    print("\nSynthetic product dynamic test passed 100%.")
