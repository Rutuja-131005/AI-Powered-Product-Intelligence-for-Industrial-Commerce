"""
Record Mapper to Exact 252 Headers
"""

from typing import Dict, Any, List
from .output_schema import FINAL_252_HEADERS

def map_record_to_252_columns(enriched_data: Dict[str, Any], raw_input: Dict[str, Any]) -> Dict[str, str]:
    """Ensures every single one of the 252 headers is present and non-null."""
    row: Dict[str, str] = {}
    
    # 1. Source Inputs (100% preservation)
    row["Mfg_Part_Num"] = str(raw_input.get("Mfg_Part_Num", ""))
    row["Part_Desc"] = str(raw_input.get("Part_Desc", ""))
    row["E1_Brand"] = str(raw_input.get("E1_Brand", ""))
    row["Unilog_Brand"] = str(raw_input.get("Unilog_Brand", ""))
    row["DIB_Brand"] = str(raw_input.get("DIB_Brand", ""))
    row["Part_Manuf"] = str(raw_input.get("Part_Manuf", ""))

    # 2. Map all enriched fields
    for header in FINAL_252_HEADERS:
        if header not in row:
            val = enriched_data.get(header)
            # Check lowercase / alternative casing in enriched data
            if val is None:
                val = enriched_data.get(header.lower(), enriched_data.get(header.title(), ""))
            row[header] = "" if val is None else str(val)

    return row
