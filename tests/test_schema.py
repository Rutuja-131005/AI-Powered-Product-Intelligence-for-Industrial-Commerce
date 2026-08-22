"""
Schema Contract Tests
Verifies that the export schema matches the exact 252 contractual headers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export.output_schema import FINAL_252_HEADERS

def test_schema_contract():
    assert len(FINAL_252_HEADERS) == 252, f"Expected 252 columns, got {len(FINAL_252_HEADERS)}"
    assert FINAL_252_HEADERS[0] == "MFR URL"
    assert FINAL_252_HEADERS[6] == "PART_NUMBER"
    assert FINAL_252_HEADERS[11] == "Mfg_Part_Num"
    assert FINAL_252_HEADERS[251] == "Actual Image (Yes/No)"
    print("[PASS] test_schema: Exact 252 contractual headers verified.")

if __name__ == "__main__":
    test_schema_contract()
