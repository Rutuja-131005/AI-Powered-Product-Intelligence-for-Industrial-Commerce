"""
Integration Tests for FastAPI Backend Endpoints
"""

import sys
import os
import io
import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from db.models import Job, Product
from export.output_schema import FINAL_252_HEADERS

client = TestClient(app)

def test_api_jobs_flow():
    # 1. Prepare sample CSV bytes
    df = pd.DataFrame([
        {
            "Mfg_Part_Num": "140U-J0D3-C40",
            "Part_Desc": "CIR BRKR 40A 3P 600V MOLDED CASE",
            "E1_Brand": "ALLEN BRADLEY",
            "Unilog_Brand": "Allen-Bradley",
            "DIB_Brand": "ROCKWELL",
            "Part_Manuf": "Rockwell Automation"
        }
    ])
    csv_buf = io.BytesIO()
    df.to_csv(csv_buf, index=False)
    csv_buf.seek(0)

    # 2. Upload file to POST /api/jobs
    res = client.post("/api/jobs", files={"file": ("test_upload.csv", csv_buf, "text/csv")})
    assert res.status_code == 200, f"Upload failed: {res.text}"
    job_data = res.json()
    job_id = job_data["job_id"]
    assert job_data["total_rows"] == 1
    print(f"[PASS] POST /api/jobs succeeded. Job ID: {job_id}")

    # 3. GET /api/jobs/{job_id}
    res_status = client.get(f"/api/jobs/{job_id}")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["job_id"] == job_id
    print("[PASS] GET /api/jobs/{job_id} verified.")

    # 4. GET /api/jobs/{job_id}/products
    res_prods = client.get(f"/api/jobs/{job_id}/products")
    assert res_prods.status_code == 200
    print("[PASS] GET /api/jobs/{job_id}/products verified.")

    # 5. GET /api/review-queue
    res_queue = client.get("/api/review-queue")
    assert res_queue.status_code == 200
    print("[PASS] GET /api/review-queue verified.")

    # 6. GET /api/jobs/{job_id}/export/csv
    res_csv = client.get(f"/api/jobs/{job_id}/export/csv")
    if res_csv.status_code == 200:
        csv_df = pd.read_csv(io.BytesIO(res_csv.content))
        assert len(csv_df.columns) == 252
        print("[PASS] GET /api/jobs/{job_id}/export/csv verified (252 headers).")

if __name__ == "__main__":
    test_api_jobs_flow()
    print("API Endpoint tests passed 100%.")
