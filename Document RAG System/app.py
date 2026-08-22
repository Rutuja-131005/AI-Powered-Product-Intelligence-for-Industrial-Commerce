from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import shutil
import os
import io
import pandas as pd
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ingest import ingest_file, get_collection_stats, delete_file_embeddings
from rag import query_rag
from history import get_all_chats, get_chat, delete_chat, save_chat

from product_intelligence.pipeline import get_pipeline_instance
from product_intelligence.schema import EXPECTED_OUTPUT_COLUMNS, NUM_OUTPUT_COLUMNS
from product_intelligence.exporter import export_to_csv_bytes, export_to_xlsx_bytes
from sample_generator import generate_sample_csv

app = FastAPI(title="AI-Powered Product Intelligence & Document RAG Platform")

os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files_static", StaticFiles(directory="data"), name="files_static")

pipeline = get_pipeline_instance()

# ----------------- Document RAG Endpoints -----------------

class QueryRequest(BaseModel):
    query: str
    history: list[dict] = []

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
            
        # Run ingestion in background
        background_tasks.add_task(background_ingest, file_location)
        
        return JSONResponse(content={"message": f"Upload accepted. Processing {file.filename} in background."}, status_code=200)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Upload failed: {e}")
        return JSONResponse(content={"message": str(e)}, status_code=500)

@app.get("/files")
async def list_files():
    files = []
    if os.path.exists("data"):
        for f in os.listdir("data"):
            if os.path.isfile(os.path.join("data", f)) and not f.endswith(".csv"):
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
    else:
        return JSONResponse(content={"message": "File deleted from disk but failed to remove from DB"}, status_code=500)

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    response_data = query_rag(request.query, request.history)
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
async def delete_chat_history(chat_id: str):
    success = delete_chat(chat_id)
    if success:
        return {"message": "Chat deleted"}
    return JSONResponse(content={"message": "Chat not found"}, status_code=404)

class SaveChatRequest(BaseModel):
    id: str
    title: str
    messages: list[dict]

@app.post("/history")
async def save_chat_history_endpoint(request: SaveChatRequest):
    save_chat(request.id, request.title, request.messages)
    return {"message": "Chat saved"}


# ------------- Product Intelligence REST API Endpoints -------------

@app.post("/api/intelligence/upload")
async def upload_catalog_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Accepts arbitrary CSV or XLSX sparse catalog file and queues enrichment."""
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith(".csv") or filename.endswith(".txt"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file format. Please upload CSV or XLSX."})
        
        if df.empty:
            return JSONResponse(status_code=400, content={"error": "Uploaded file is empty."})
        
        job_id = pipeline.create_job(df, filename=file.filename)
        background_tasks.add_task(pipeline.run_batch_job, job_id)
        
        return {
            "message": "File uploaded and batch enrichment job started.",
            "job_id": job_id,
            "filename": file.filename,
            "total_rows": len(df),
            "expected_columns": NUM_OUTPUT_COLUMNS
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to parse file: {str(e)}"})

@app.post("/api/intelligence/demo/load")
async def load_sample_dataset(background_tasks: BackgroundTasks, rows: int = 100):
    """Loads realistic industrial sample dataset for immediate testing and demo."""
    try:
        sample_path = "data/sample_industrial_input.csv"
        if not os.path.exists(sample_path):
            generate_sample_csv(sample_path, total_rows=1000)
            
        df = pd.read_csv(sample_path)
        if rows < len(df):
            df = df.iloc[:rows].copy()
            
        job_id = pipeline.create_job(df, filename=f"sample_industrial_{rows}_rows.csv")
        background_tasks.add_task(pipeline.run_batch_job, job_id)
        
        return {
            "message": f"Loaded {len(df)} sample industrial parts. Enrichment started.",
            "job_id": job_id,
            "filename": f"sample_industrial_{rows}_rows.csv",
            "total_rows": len(df)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/intelligence/status/{job_id}")
async def get_job_progress(job_id: str):
    """Returns real-time progress, processed counts, and quality KPIs."""
    status = pipeline.get_job_status(job_id)
    if not status:
        return JSONResponse(status_code=404, content={"error": "Job ID not found."})
    return status

@app.get("/api/intelligence/products/{job_id}")
async def get_job_products(
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

@app.get("/api/intelligence/product/{job_id}/{row_idx}")
async def get_single_product_detail(job_id: str, row_idx: int):
    """Returns detailed product record with 50 triplets, evidence citations, and provenance."""
    job = pipeline.jobs.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    records = job.get("records", [])
    if row_idx < 0 or row_idx >= len(records):
        return JSONResponse(status_code=404, content={"error": "Product index out of bounds"})
    return records[row_idx]

class FieldUpdateRequest(BaseModel):
    field_name: str
    new_value: str

@app.post("/api/intelligence/product/{job_id}/{row_idx}/update")
async def update_product_field_endpoint(job_id: str, row_idx: int, req: FieldUpdateRequest):
    """Updates / approves a field by human reviewer."""
    success = pipeline.update_product_field(job_id, row_idx, req.field_name, req.new_value)
    if success:
        return {"message": "Field updated successfully", "field": req.field_name, "value": req.new_value}
    return JSONResponse(status_code=400, content={"error": "Failed to update field"})

@app.get("/api/intelligence/export/{job_id}/csv")
async def export_job_csv(job_id: str):
    """Exports exact 252-column CSV file."""
    job = pipeline.jobs.get(job_id)
    if not job or not job.get("records"):
        return JSONResponse(status_code=404, content={"error": "No records available to export"})
    
    csv_bytes = export_to_csv_bytes(job["records"])
    filename = f"Enriched_Product_Catalog_252_Cols_{job_id}.csv"
    
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/intelligence/export/{job_id}/xlsx")
async def export_job_xlsx(job_id: str):
    """Exports exact 252-column XLSX workbook."""
    job = pipeline.jobs.get(job_id)
    if not job or not job.get("records"):
        return JSONResponse(status_code=404, content={"error": "No records available to export"})
    
    xlsx_bytes = export_to_xlsx_bytes(job["records"])
    filename = f"Enriched_Product_Catalog_252_Cols_{job_id}.xlsx"
    
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.post("/api/intelligence/cancel/{job_id}")
async def cancel_job(job_id: str):
    job = pipeline.jobs.get(job_id)
    if job:
        job["status"] = "CANCELLED"
        return {"message": "Job cancellation requested"}
    return JSONResponse(status_code=404, content={"error": "Job not found"})

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8000 ...")
    uvicorn.run(app, host="localhost", port=8000)