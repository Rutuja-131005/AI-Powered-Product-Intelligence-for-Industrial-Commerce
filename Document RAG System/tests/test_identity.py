"""
Test Identity Resolution & Exporter
"""

import sys
import os
import io
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product.identity import resolve_product_identity
from export.output_schema import FINAL_252_HEADERS
from export.exporter import export_catalog_to_csv, export_catalog_to_xlsx
from jobs.processor import JobProcessor

def test_identity():
    ident = resolve_product_identity(
        mfg_part_num="140U-J0D3-C40",
        part_desc="CIR BRKR 40A 3P 600V",
        e1_brand="ALLEN BRADLEY",
        unilog_brand="Allen-Bradley",
        dib_brand="ROCKWELL",
        part_manuf="Rockwell Automation"
    )
    assert ident["Resolved_Brand"] == "Allen-Bradley"
    assert ident["Canonical_Part_Number"] == "140U-J0D3-C40"
    print("[PASS] Identity resolved successfully.")

def test_export():
    row = {
        "Mfg_Part_Num": "140U-J0D3-C40",
        "Part_Desc": "CIR BRKR 40A 3P 600V",
        "E1_Brand": "ALLEN BRADLEY",
        "Unilog_Brand": "Allen-Bradley",
        "DIB_Brand": "ROCKWELL",
        "Part_Manuf": "Rockwell Automation"
    }
    processed = JobProcessor.process_single_row(row, 0)
    
    csv_bytes = export_catalog_to_csv([processed])
    df_csv = pd.read_csv(io.BytesIO(csv_bytes))
    assert list(df_csv.columns) == FINAL_252_HEADERS
    assert len(df_csv) == 1
    
    xlsx_bytes = export_catalog_to_xlsx([processed])
    df_xlsx = pd.read_excel(io.BytesIO(xlsx_bytes))
    assert list(df_xlsx.columns) == FINAL_252_HEADERS
    assert len(df_xlsx) == 1
    print("[PASS] Export to 252-column CSV & XLSX confirmed.")

if __name__ == "__main__":
    test_identity()
    test_export()
    print("All modular tests passed 100%.")
