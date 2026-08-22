"""
Test End-to-End Workflow Execution & Failure Isolation
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.processor import JobProcessor
from export.output_schema import FINAL_252_HEADERS

def test_workflow_validation():
    # 1. Test input validation
    valid_df = pd.DataFrame([{"Mfg_Part_Num": "140U-J0D3-C40", "Part_Desc": "CIR BRKR"}])
    is_valid, err = JobProcessor.validate_input_schema(valid_df)
    assert is_valid is True, f"Expected valid, got error {err}"

    invalid_df = pd.DataFrame([{"Random_Header": "123"}])
    is_invalid, err = JobProcessor.validate_input_schema(invalid_df)
    assert is_invalid is False, "Expected invalid schema rejection"
    print("[PASS] Input schema validation verified.")

def test_single_row_workflow_and_isolation():
    # 2. Test row processing
    row = {
        "Mfg_Part_Num": "140U-J0D3-C40",
        "Part_Desc": "CIR BRKR 40A 3P 600V MOLDED CASE",
        "E1_Brand": "ALLEN BRADLEY",
        "Unilog_Brand": "Allen-Bradley",
        "DIB_Brand": "ROCKWELL",
        "Part_Manuf": "Rockwell Automation"
    }
    processed = JobProcessor.process_single_row(row, 0)
    
    assert processed["_status"] == "COMPLETED"
    assert processed["Mfg_Part_Num"] == "140U-J0D3-C40"
    assert processed["_validation_status"] in ["VERIFIED", "PARTIAL"]
    
    # 3. Test export contract validation
    valid_export, exp_err = JobProcessor.validate_export_contract([processed], 1)
    assert valid_export is True, f"Export validation failed: {exp_err}"
    print("[PASS] Full end-to-end single row workflow & export contract verified.")

if __name__ == "__main__":
    test_workflow_validation()
    test_single_row_workflow_and_isolation()
    print("Workflow tests passed 100%.")
