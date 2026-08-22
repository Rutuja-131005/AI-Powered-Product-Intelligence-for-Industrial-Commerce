"""
Pipeline Integration Tests
Verifies the end-to-end execution of the ProductPipeline.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.product_pipeline import ProductPipeline

def test_pipeline_execution():
    raw_item = {
        "Mfg_Part_Num": "DCF860B",
        "Part_Desc": "Dewalt 20V MAX XR 1/4 In. 3-Speed Impact Driver",
        "E1_Brand": "DEWALT",
        "Unilog_Brand": "Dewalt",
        "DIB_Brand": "DEWALT",
        "Part_Manuf": "Dewalt Industrial Tool Co."
    }
    result = ProductPipeline.process_single_row(raw_item)
    assert result["PART_NUMBER"] == "DCF860B"
    assert result["BRAND_NAME"] == "Dewalt"
    assert len(result) >= 252
    print("[PASS] test_pipeline: ProductPipeline executed and produced 252-column schema.")

if __name__ == "__main__":
    test_pipeline_execution()
