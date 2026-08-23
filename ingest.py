"""
Document Ingestion & Indexing Engine with Product Metadata Support
Supports PDF, DOCX, TXT with section-aware chunking and ChromaDB persistence.
"""

import os
import glob
import hashlib
import pypdf
import docx

from chroma_cloud_client import (
    get_chroma_client as get_client,
    get_embedding_function as get_ef,
    chunk_text_line_based,
    DEFAULT_COLLECTION as COLLECTION_NAME,
    CHROMA_HOST,
    CHROMA_TENANT,
    CHROMA_DATABASE,
    CHROMA_API_KEY
)

CHROMA_PATH = "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"

def parse_pdf(file_path):
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text += f"\n--- Page {page_num + 1} ---\n" + page_text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def parse_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def parse_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext == ".txt":
        return parse_txt(file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return ""

def split_text(text, chunk_size=1000, overlap=200):
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def ingest_file(file_path, extra_metadata: dict = None):
    filename = os.path.basename(file_path)
    print(f"Ingesting file: {filename}")
    
    text = load_file(file_path)
    if not text:
        print(f"ERROR: No text extracted from {filename}")
        return False
    
    chunks = split_text(text)
    if not chunks:
        print("ERROR: No chunks created")
        return False

    chunked_texts = []
    metadatas = []
    ids = []
    content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    for i, chunk in enumerate(chunks):
        chunked_texts.append(chunk)
        meta = {
            "source": filename,
            "chunk_id": i,
            "content_hash": content_hash,
            "source_type": extra_metadata.get("source_type", "SPEC_SHEET") if extra_metadata else "SPEC_SHEET"
        }
        if extra_metadata:
            meta.update(extra_metadata)
            
        metadatas.append(meta)
        ids.append(f"{filename}_{i}")

    client = get_client()
    ef = get_ef()
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

    collection.upsert(
        documents=chunked_texts,
        metadatas=metadatas,
        ids=ids
    )
    return True

def ingest_directory(directory="data"):
    files = glob.glob(os.path.join(directory, "*"))
    for f in files:
        if os.path.isfile(f) and not f.endswith(".csv") and not f.endswith(".db"):
            ingest_file(f)

def get_collection_stats():
    try:
        if not os.path.exists(CHROMA_PATH):
            return 0
        client = get_client()
        try:
            collection = client.get_collection(name=COLLECTION_NAME)
            return collection.count()
        except (ValueError, Exception):
            return 0
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 0

def delete_file_embeddings(filename):
    try:
        if not os.path.exists(CHROMA_PATH):
            return True
        client = get_client()
        collection = client.get_collection(name=COLLECTION_NAME)
        collection.delete(where={"source": filename})
        return True
    except Exception as e:
        print(f"Error deleting embeddings for {filename}: {e}")
        return False

if __name__ == "__main__":
    ingest_directory()
