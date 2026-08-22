"""
Catalog Export Engine for 252-Column CSV and XLSX Files
Strict schema compliance, correct order, no extraneous metadata columns.
"""

import io
import pandas as pd
from typing import List, Dict, Any
from .schema import EXPECTED_OUTPUT_COLUMNS

def export_to_csv_bytes(records: List[Dict[str, Any]]) -> bytes:
    """
    Exports product records to CSV bytes with exactly the 252 expected headers
    in strict sequence.
    """
    clean_rows = []
    for r in records:
        clean_row = {}
        for col in EXPECTED_OUTPUT_COLUMNS:
            val = r.get(col, "")
            clean_row[col] = "" if val is None else str(val)
        clean_rows.append(clean_row)

    df = pd.DataFrame(clean_rows, columns=EXPECTED_OUTPUT_COLUMNS)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8")
    return output.getvalue().encode("utf-8")

def export_to_xlsx_bytes(records: List[Dict[str, Any]]) -> bytes:
    """
    Exports product records to XLSX bytes with exactly the 252 expected headers
    in strict sequence using openpyxl.
    """
    clean_rows = []
    for r in records:
        clean_row = {}
        for col in EXPECTED_OUTPUT_COLUMNS:
            val = r.get(col, "")
            clean_row[col] = "" if val is None else str(val)
        clean_rows.append(clean_row)

    df = pd.DataFrame(clean_rows, columns=EXPECTED_OUTPUT_COLUMNS)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Enriched_Catalog")
    
    return output.getvalue()
