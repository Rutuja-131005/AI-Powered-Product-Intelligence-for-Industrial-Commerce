"""
CSV and XLSX Exporter Module
"""

import io
import pandas as pd
from typing import List, Dict, Any
from .output_schema import FINAL_252_HEADERS

def export_catalog_to_csv(rows: List[Dict[str, Any]]) -> bytes:
    """Exports rows to UTF-8 RFC 4180 CSV bytes with exact 252 headers."""
    df = pd.DataFrame(rows, columns=FINAL_252_HEADERS)
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8")
    return output.getvalue().encode("utf-8")

def export_catalog_to_xlsx(rows: List[Dict[str, Any]]) -> bytes:
    """Exports rows to OpenPyXL XLSX bytes with exact 252 headers."""
    df = pd.DataFrame(rows, columns=FINAL_252_HEADERS)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Enriched_Catalog_252")
    return output.getvalue()
