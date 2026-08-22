"""
Test 252 Schema Compliance and Fixed Contract
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.output_schema import FINAL_252_HEADERS, GROUP_1_SOURCE_INPUT

def test_252_headers_count():
    assert len(FINAL_252_HEADERS) == 252, f"Expected 252 headers, found {len(FINAL_252_HEADERS)}"
    print("[PASS] Exact 252 headers confirmed.")

def test_source_preservation_contract():
    expected_sources = ["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"]
    assert FINAL_252_HEADERS[:6] == expected_sources, "Initial 6 headers must be the source input fields"
    print("[PASS] Source input preservation confirmed.")

if __name__ == "__main__":
    test_252_headers_count()
    test_source_preservation_contract()
    print("Schema tests passed 100%.")
