from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Query, Response, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import shutil
import os
import io
import csv
import time
import uuid
import pandas as pd
from typing import Optional, List, Dict, Any

from ingest import ingest_file, get_collection_stats, delete_file_embeddings
from rag import query_rag
from history import get_all_chats, get_chat, delete_chat, save_chat

from db.database import get_db, SessionLocal
from db.models import Job, Product, ProductAttribute, Source, Evidence, ValidationResult, Review, ProductAsset
from db.schemas import (
    JobCreateResponse, JobStatusResponse, ReviewAction,
    ProductIntelligence, ExportValidationResult
)

from product_intelligence.pipeline import get_pipeline_instance
from product_intelligence.schema import EXPECTED_OUTPUT_COLUMNS, NUM_OUTPUT_COLUMNS
from product_intelligence.exporter import export_to_csv_bytes, export_to_xlsx_bytes
from sample_generator import generate_sample_csv
from jobs.processor import JobProcessor
from export.output_schema import FINAL_252_HEADERS
from export.exporter import export_catalog_to_csv, export_catalog_to_xlsx

app = FastAPI(title="AI-Powered Product Intelligence for Industrial Commerce")

os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files_static", StaticFiles(directory="data"), name="files_static")

pipeline = get_pipeline_instance()

# ----------------- Document RAG Endpoints -----------------

class QueryRequest(BaseModel := type('QueryRequest', (object,), {
    '__annotations__': {'query': str, 'history': list[dict]},
    'history': []
})):
    pass

@app.get("/")
async def read_root():
    return FileResponse('templates/index.html')

def background_ingest(file_location):
    ingest_file(file_location)

@app.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_location = f"data/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        background_tasks.add_task(background_ingest, file_location)
        return JSONResponse(content={"message": f"Upload accepted. Processing {file.filename} in background."}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

@app.get("/files")
async def list_files():
    files = []
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if os.path.isfile(os.path.join("data", f)) and not f.endswith(".csv") and not f.endswith(".db"):
                 files.append(f)
    return files

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join("data", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        return JSONResponse(content={"message": "File not found on disk"}, status_code=404)
        
    success = delete_file_embeddings(filename)
    if success:
        return {"message": f"Deleted {filename}"}
    return JSONResponse(content={"message": "File deleted from disk but failed to remove from DB"}, status_code=500)

@app.post("/query")
async def query_endpoint(request: Dict[str, Any]):
    query_text = request.get("query", "")
    hist = request.get("history", [])
    response_data = query_rag(query_text, hist)
    return response_data

@app.get("/status")
async def get_status():
    count = get_collection_stats()
    return {"status": "running", "chunk_count": count}

@app.get("/history")
async def get_history():
    return get_all_chats()

@app.get("/history/{chat_id}")
async def get_chat_history(chat_id: str):
    chat = get_chat(chat_id)
    if chat:
        return chat
    return JSONResponse(content={"message": "Chat not found"}, status_code=404)

@app.delete("/history/{chat_id}")
async def delete_chat_history_endpoint(chat_id: str):
    success = delete_chat(chat_id)
    if success:
        return {"message": "Chat deleted"}
    return JSONResponse(content={"message": "Chat not found"}, status_code=404)

@app.post("/history")
async def save_chat_history_endpoint(request: Dict[str, Any]):
    save_chat(request.get("id", ""), request.get("title", ""), request.get("messages", []))
    return {"message": "Chat saved"}


# ----------------- AI Product Intelligence Endpoints (TRD Schema Compliant) -----------------

@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads sparse CSV/XLSX, validates schema, persists job, and triggers enrichment."""
    try:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".csv") or filename.endswith(".txt"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Please upload CSV or XLSX.")

        is_valid, err_msg = JobProcessor.validate_input_schema(df)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Input schema validation failed: {err_msg}")

        job_id = pipeline.create_job(df, filename=file.filename)
        background_tasks.add_task(pipeline.run_batch_job, job_id)

        # Persist in DB
        db_job = Job(
            id=job_id,
            filename=file.filename,
            total_rows=len(df),
            status="PROCESSING"
        )
        db.add(db_job)
        db.commit()

        return JobCreateResponse(
            job_id=job_id,
            filename=file.filename,
            status="PROCESSING",
            total_rows=len(df),
            message="Job created and enrichment started successfully."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status_endpoint(job_id: str):
    """Returns detailed job status, row counts, and progress telemetry."""
    status = pipeline.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job ID not found.")

    return JobStatusResponse(
        job_id=status["job_id"],
        filename=status["filename"],
        status=status["status"],
        total_rows=status["total_rows"],
        processed_rows=status["processed_rows"],
        success_rows=status["verified_count"],
        review_rows=status["needs_review_count"],
        failed_rows=status["failed_rows"],
        progress_percent=status["progress_percent"],
        elapsed_seconds=status["elapsed_seconds"],
        error_message=status.get("error")
    )

@app.post("/api/jobs/{job_id}/start")
async def start_job_endpoint(job_id: str, background_tasks: BackgroundTasks):
    job = pipeline.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    background_tasks.add_task(pipeline.run_batch_job, job_id)
    return {"message": "Job started", "job_id": job_id}

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job_endpoint(job_id: str):
    job = pipeline.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["status"] = "CANCELLED"
    return {"message": "Job cancellation requested", "job_id": job_id}

@app.get("/api/jobs/{job_id}/products")
async def get_job_products_endpoint(
    job_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search term across PN, Desc, Brand"),
    brand: str = Query("ALL", description="Filter by brand"),
    status: str = Query("ALL", description="Filter by validation status")
):
    """Returns paginated, searchable, filterable product records."""
    data = pipeline.get_job_products(
        job_id=job_id,
        page=page,
        page_size=page_size,
        search_query=search,
        brand_filter=brand,
        status_filter=status
    )
    return data

@app.get("/api/products/{product_id}")
async def get_single_product_endpoint(product_id: int, job_id: Optional[str] = None):
    """Returns canonical product object with evidence and validation results."""
    # Find across jobs or by job_id
    target_job = pipeline.jobs.get(job_id) if job_id else next(iter(pipeline.jobs.values()), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="No active jobs found")
    records = target_job.get("records", [])
    if product_id < 0 or product_id >= len(records):
        raise HTTPException(status_code=404, detail="Product ID out of bounds")
    return records[product_id]

@app.post("/api/products/{product_id}/reprocess")
async def reprocess_product_endpoint(product_id: int, job_id: Optional[str] = None):
    """Re-executes enrichment pipeline on a single product."""
    target_job = pipeline.jobs.get(job_id) if job_id else next(iter(pipeline.jobs.values()), None)
    if not target_job or not target_job.get("records"):
        raise HTTPException(status_code=404, detail="Job not found")
    if product_id < 0 or product_id >= len(target_job["records"]):
        raise HTTPException(status_code=404, detail="Product ID out of bounds")

    raw_row = target_job["raw_dataframe"].iloc[product_id].to_dict()
    enriched = pipeline.enrich_single_product(raw_row, row_idx=product_id)
    target_job["records"][product_id] = enriched
    return {"message": "Product reprocessed successfully", "product": enriched}

@app.get("/api/review-queue")
async def get_review_queue_endpoint():
    """Retrieves all products currently flagged as NEEDS_REVIEW across active jobs."""
    review_queue = []
    for job_id, job in pipeline.jobs.items():
        for r in job.get("records", []):
            if r.get("Validation_Status") in ["NEEDS_REVIEW", "PARTIAL", "FAILED"] or r.get("Review_Status") == "NEEDS_REVIEW":
                review_queue.append({
                    "job_id": job_id,
                    "row_idx": r.get("_row_idx", 0),
                    "part_number": r.get("Mfg_Part_Num", ""),
                    "brand": r.get("Resolved_Brand", ""),
                    "title": r.get("Product_Title", ""),
                    "confidence": r.get("Overall_Confidence_Score", "0.00"),
                    "status": r.get("Validation_Status", "NEEDS_REVIEW")
                })
    return {"count": len(review_queue), "items": review_queue}

@app.post("/api/products/{product_id}/review")
async def submit_product_review_endpoint(product_id: int, review: ReviewAction, job_id: Optional[str] = None):
    """Submits a human review action (Approve, Edit, Reject)."""
    target_job = pipeline.jobs.get(job_id) if job_id else next(iter(pipeline.jobs.values()), None)
    if not target_job or product_id >= len(target_job.get("records", [])):
        raise HTTPException(status_code=404, detail="Product not found")

    rec = target_job["records"][product_id]
    rec[review.field_name] = review.new_value
    rec["Review_Status"] = review.action.upper()
    if review.action.upper() == "APPROVE":
        rec["Validation_Status"] = "VERIFIED"

    return {"message": f"Review action '{review.action}' applied successfully", "field": review.field_name, "value": review.new_value}

@app.get("/api/products/{product_id}/sources")
async def get_product_sources_endpoint(product_id: int, job_id: Optional[str] = None):
    """Returns discovered URLs and source metadata for the product."""
    prod = await get_single_product_endpoint(product_id, job_id)
    sources = [
        {"title": "Manufacturer Portal", "url": prod.get("Manufacturer_Product_URL", "")},
        {"title": "Spec Sheet / Datasheet", "url": prod.get("Spec_Sheet_URL", "")},
        {"title": "User Manual", "url": prod.get("User_Manual_URL", "")},
        {"title": "3D CAD Drawing", "url": prod.get("CAD_Drawing_URL", "")},
        {"title": "SDS / MSDS", "url": prod.get("SDS_MSDS_URL", "")},
        {"title": "Grainger Catalog", "url": prod.get("Distributor_URL_1", "")},
        {"title": "Radwell Reference", "url": prod.get("Distributor_URL_2", "")},
        {"title": "GlobalSpec Reference", "url": prod.get("Reference_Source_URL", "")}
    ]
    return {"sources": [s for s in sources if s["url"]]}

@app.get("/api/products/{product_id}/evidence")
async def get_product_evidence_endpoint(product_id: int, job_id: Optional[str] = None):
    """Returns RAG evidence chunks and citations for the product."""
    prod = await get_single_product_endpoint(product_id, job_id)
    return {"evidence": prod.get("_rag_evidence", [])}

@app.get("/api/jobs/{job_id}/export/csv")
async def export_job_csv_endpoint(job_id: str):
    """Exports exact 252-column CSV file."""
    job = pipeline.jobs.get(job_id)
    if not job or not job.get("records"):
        raise HTTPException(status_code=404, detail="No records available to export")

    csv_bytes = export_to_csv_bytes(job["records"])
    filename = f"Enriched_Product_Catalog_252_Cols_{job_id}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/jobs/{job_id}/export/xlsx")
async def export_job_xlsx_endpoint(job_id: str):
    """Exports exact 252-column XLSX workbook."""
    job = pipeline.jobs.get(job_id)
    if not job or not job.get("records"):
        raise HTTPException(status_code=404, detail="No records available to export")

    xlsx_bytes = export_to_xlsx_bytes(job["records"])
    filename = f"Enriched_Product_Catalog_252_Cols_{job_id}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# Compatibility Aliases for UI
@app.post("/api/intelligence/upload")
async def alias_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await create_job_endpoint(background_tasks, file, db)

@app.get("/api/intelligence/status/{job_id}")
async def alias_status(job_id: str):
    return await get_job_status_endpoint(job_id)

@app.get("/api/intelligence/products/{job_id}")
async def alias_products(job_id: str, page: int = Query(1), page_size: int = Query(20), search: str = Query(""), brand: str = Query("ALL"), status: str = Query("ALL")):
    return await get_job_products_endpoint(job_id, page, page_size, search, brand, status)

@app.get("/api/intelligence/product/{job_id}/{row_idx}")
async def alias_product_detail(job_id: str, row_idx: int):
    return await get_single_product_endpoint(row_idx, job_id)

@app.post("/api/intelligence/product/{job_id}/{row_idx}/update")
async def alias_update_field(job_id: str, row_idx: int, req: Dict[str, Any]):
    action = ReviewAction(field_name=req.get("field_name", ""), new_value=req.get("new_value", ""), action="EDIT")
    return await submit_product_review_endpoint(row_idx, action, job_id)

@app.get("/api/intelligence/export/{job_id}/{format}")
async def alias_export(job_id: str, format: str):
    if format == "csv":
        return await export_job_csv_endpoint(job_id)
    return await export_job_xlsx_endpoint(job_id)

@app.post("/api/intelligence/demo/load")
async def load_sample_dataset_endpoint(background_tasks: BackgroundTasks, rows: int = 100):
    dataset_file = "dataset.csv"
    if not os.path.exists(dataset_file):
        dataset_file = "data/dataset.csv"
    
    rows_data = []
    with open(dataset_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows_data.append(row)
            if rows and len(rows_data) >= rows:
                break
    df = pd.DataFrame(rows_data)
    job_id = pipeline.create_job(df, filename=f"dataset_{len(df)}_rows.csv")
    background_tasks.add_task(pipeline.run_batch_job, job_id)
    return {"message": f"Loaded {len(df)} parts from dataset.csv.", "job_id": job_id, "total_rows": len(df)}

# ----------------- Multimodal Image/PDF & Google Sheets Integration -----------------
from sources.multimodal_analyzer import MultimodalProductAnalyzer
from db.sheets_sync import GoogleSheetsSync, SPREADSHEET_URL, APPS_SCRIPT_WEBAPP_URL

@app.post("/api/intelligence/upload-image")
async def upload_product_image_endpoint(file: UploadFile = File(...)):
    """Accepts product image, performs OCR/visual spec analysis, discovers websites, and syncs to Google Sheets."""
    content = await file.read()
    mapped_product = MultimodalProductAnalyzer.analyze_image(content, filename=file.filename)
    
    # Store in default active job or create standalone record
    default_job = next(iter(pipeline.jobs.values()), None)
    if not default_job:
        df = pd.DataFrame([mapped_product])
        job_id = pipeline.create_job(df, filename=f"Image_Upload_{file.filename}")
        default_job = pipeline.jobs[job_id]
        default_job["records"] = [mapped_product]
        default_job["status"] = "COMPLETED"
        default_job["processed_rows"] = 1
        default_job["success_rows"] = 1
    else:
        default_job["records"].insert(0, mapped_product)
        default_job["total_rows"] += 1
        default_job["processed_rows"] += 1
        default_job["success_rows"] += 1

    return {
        "status": "success",
        "message": f"Product image {file.filename} analyzed successfully across authoritative web sources.",
        "product": mapped_product,
        "spreadsheet_url": SPREADSHEET_URL,
        "sheets_sync": mapped_product.get("_sheets_sync")
    }

@app.post("/api/intelligence/upload-pdf")
async def upload_product_pdf_endpoint(file: UploadFile = File(...)):
    """Accepts spec sheet / manual PDF, extracts specs, discovers websites, and syncs to Google Sheets."""
    content = await file.read()
    mapped_product = MultimodalProductAnalyzer.analyze_pdf(content, filename=file.filename)

    default_job = next(iter(pipeline.jobs.values()), None)
    if not default_job:
        df = pd.DataFrame([mapped_product])
        job_id = pipeline.create_job(df, filename=f"PDF_Upload_{file.filename}")
        default_job = pipeline.jobs[job_id]
        default_job["records"] = [mapped_product]
        default_job["status"] = "COMPLETED"
        default_job["processed_rows"] = 1
        default_job["success_rows"] = 1
    else:
        default_job["records"].insert(0, mapped_product)
        default_job["total_rows"] += 1
        default_job["processed_rows"] += 1
        default_job["success_rows"] += 1

    return {
        "status": "success",
        "message": f"Technical specification PDF {file.filename} analyzed successfully.",
        "product": mapped_product,
        "spreadsheet_url": SPREADSHEET_URL,
        "sheets_sync": mapped_product.get("_sheets_sync")
    }

@app.post("/api/sync/sheets")
async def sync_all_to_sheets_endpoint(job_id: Optional[str] = None):
    """Syncs all processed catalog products and discovered analysis URLs to Google Sheets."""
    target_job = pipeline.jobs.get(job_id) if job_id else next(iter(pipeline.jobs.values()), None)
    if not target_job or not target_job.get("records"):
        raise HTTPException(status_code=404, detail="No catalog records available to sync")

    records = target_job["records"]
    sync_summary = GoogleSheetsSync.sync_batch(records)
    return {
        "status": "success",
        "message": f"Synchronized {sync_summary['total_synced']} products & {sync_summary['analysis_links_collected']} analysis links to Google Sheets.",
        "spreadsheet_url": SPREADSHEET_URL,
        "webapp_url": APPS_SCRIPT_WEBAPP_URL,
        "details": sync_summary
    }

@app.get("/api/sync/sheets/status")
async def get_sheets_sync_status_endpoint():
    """Returns Google Spreadsheet configuration & sync status."""
    return {
        "spreadsheet_url": SPREADSHEET_URL,
        "webapp_url": APPS_SCRIPT_WEBAPP_URL,
        "deployment_id": "AKfycbzsTAE29OcKiX8zDOj8HlbIO_WHjMR0v8u84YflQHYLyqfr0ai0KiFJATl49KLQfktfQ",
        "connected": True
    }

from sources.research_service import ProductResearchService

@app.post("/api/intelligence/search-product")
async def search_and_research_product_endpoint(request: Dict[str, Any]):
    """
    Takes product search query or part number, executes multi-website research,
    saves 252-column record to backend DB and Google Sheets, and returns live research links.
    """
    query = request.get("query", "")
    brand_hint = request.get("brand", None)
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = ProductResearchService.research_query(query, brand_hint=brand_hint)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Persist in pipeline jobs store silently in backend
    default_job = next(iter(pipeline.jobs.values()), None)
    if default_job:
        default_job["records"].insert(0, result["raw_record"])
        default_job["total_rows"] += 1
        default_job["processed_rows"] += 1
        default_job["success_rows"] += 1

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)