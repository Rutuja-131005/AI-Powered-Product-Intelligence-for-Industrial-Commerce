"""
Test 252 Schema Compliance and Fixed Contract
Validates the exact 252 contractual output headers and original input preservation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.output_schema import (
    FINAL_252_HEADERS, ORIGINAL_INPUT_HEADERS,
    GROUP_1_SOURCE_URLS, GROUP_2_CORE_IDENTIFIERS,
    GROUP_3_DESCRIPTIONS, GROUP_4_FEATURES,
    GROUP_5_METADATA, GROUP_6_ATTRIBUTES,
    GROUP_7_COMMERCIAL_DIMENSIONS, GROUP_8_ASSETS_DOCUMENTS,
    GROUP_9_FLAGS
)

def test_252_headers_count():
    assert len(FINAL_252_HEADERS) == 252, f"Expected 252 headers, found {len(FINAL_252_HEADERS)}"
    print("[PASS] Exact 252 headers confirmed.")

def test_source_preservation_contract():
    # Columns 12 to 17 (0-indexed 11 to 17) must match the raw 6 inputs
    expected_sources = ["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"]
    assert FINAL_252_HEADERS[11:17] == expected_sources, "Columns 12-17 must be the raw source input fields"
    assert FINAL_252_HEADERS[0] == "MFR URL"
    assert FINAL_252_HEADERS[6] == "PART_NUMBER"
    assert FINAL_252_HEADERS[55] == "ATTRIBUTE_LABEL 1"
    assert FINAL_252_HEADERS[56] == "ATTRIBUTE_VALUE 1"
    assert FINAL_252_HEADERS[57] == "ATTRIBUTE_UOM 1"
    assert FINAL_252_HEADERS[249] == "Country Of Origin"
    assert FINAL_252_HEADERS[250] == "Discontinued"
    assert FINAL_252_HEADERS[251] == "Actual Image (Yes/No)"
    print("[PASS] Source input preservation and header sequence confirmed.")

if __name__ == "__main__":
    test_252_headers_count()
    test_source_preservation_contract()
    print("Schema tests passed 100%.")
