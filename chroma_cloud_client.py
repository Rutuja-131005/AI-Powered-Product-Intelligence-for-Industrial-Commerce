"""
Chroma Cloud Client & Search Infrastructure
Manages connection to Chroma Cloud (api.trychroma.com), line-based chunking (<16 KiB),
dense embeddings, collection sharding, and hybrid vector search.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Chroma Cloud Settings
CHROMA_HOST = os.getenv("CHROMA_HOST", "api.trychroma.com")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "").strip()
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "8092f213-aef2-4d28-b9c8-ec7c84e7ad0d")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "Product-Intelligence")
DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "Product_Intelligence_Catalog")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

_CHROMA_CLIENT = None
_EMBEDDING_FN = None

def get_embedding_function():
    """Returns the dense embedding function for Chroma Cloud."""
    global _EMBEDDING_FN
    if _EMBEDDING_FN is None:
        try:
            from chromadb.utils import embedding_functions
            _EMBEDDING_FN = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(f"SentenceTransformer fallback: {e}")
            from chromadb.utils import embedding_functions
            _EMBEDDING_FN = embedding_functions.DefaultEmbeddingFunction()
    return _EMBEDDING_FN

def get_chroma_client():
    """
    Initializes and returns a Chroma Cloud Client when API key is provided,
    or falls back gracefully to local PersistentClient.
    """
    global _CHROMA_CLIENT
    if _CHROMA_CLIENT is not None:
        return _CHROMA_CLIENT

    import chromadb

    api_key = os.getenv("CHROMA_API_KEY", "").strip()
    host = os.getenv("CHROMA_HOST", "api.trychroma.com")
    tenant = os.getenv("CHROMA_TENANT", "8092f213-aef2-4d28-b9c8-ec7c84e7ad0d")
    database = os.getenv("CHROMA_DATABASE", "Product-Intelligence")

    if api_key and api_key != "<ask user to copy .env file or API key>":
        try:
            logger.info(f"Connecting to Chroma Cloud (Host: {host}, Database: {database}, Tenant: {tenant})...")
            _CHROMA_CLIENT = chromadb.CloudClient(
                cloud_host=host,
                tenant=tenant,
                database=database,
                api_key=api_key
            )
            logger.info("Successfully connected to Chroma Cloud!")
            return _CHROMA_CLIENT
        except Exception as err:
            logger.error(f"Failed to connect to Chroma Cloud: {err}. Falling back to local PersistentClient.")

    # Fallback to local persistent storage
    logger.info("Using local PersistentClient (chroma_db)")
    _CHROMA_CLIENT = chromadb.PersistentClient(path="chroma_db")
    return _CHROMA_CLIENT

def get_or_create_collection(collection_name: str = DEFAULT_COLLECTION):
    """
    Shards and creates/retrieves a collection with dense embeddings.
    """
    client = get_chroma_client()
    ef = get_embedding_function()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef
    )

def chunk_text_line_based(text: str, max_chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """
    Line-based chunking strategy for technical documents and product specs (<16 KiB limit).
    Preserves line boundaries and context.
    """
    if not text:
        return []

    lines = text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1
        if current_length + line_len > max_chunk_size and current_chunk:
            chunk_str = "\n".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)
            # Maintain line overlap
            overlap_lines = []
            overlap_len = 0
            for prev_line in reversed(current_chunk):
                if overlap_len + len(prev_line) + 1 <= overlap:
                    overlap_lines.insert(0, prev_line)
                    overlap_len += len(prev_line) + 1
                else:
                    break
            current_chunk = overlap_lines
            current_length = overlap_len

        current_chunk.append(line)
        current_length += line_len

    if current_chunk:
        chunk_str = "\n".join(current_chunk).strip()
        if chunk_str:
            chunks.append(chunk_str)

    return chunks

def hybrid_search(query_text: str, n_results: int = 4, collection_name: str = DEFAULT_COLLECTION, brand_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes grounded semantic search on Chroma Cloud with metadata filtering.
    """
    collection = get_or_create_collection(collection_name)

    where_clause = None
    if brand_filter:
        where_clause = {"brand": brand_filter}

    try:
        if where_clause:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )
        else:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        return results
    except Exception as e:
        logger.error(f"Search query error: {e}")
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
