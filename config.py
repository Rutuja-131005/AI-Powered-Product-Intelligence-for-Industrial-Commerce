"""
Application Configuration and Settings
Manages environment variables, model parameters, timeouts, and thresholds.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'catalog.db'}")

# AI / Model Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "rag_collection")

# Batch Processing & Rate Limits
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "10"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

# Confidence Thresholds
CONFIDENCE_HIGH_THRESHOLD = 0.85
CONFIDENCE_MEDIUM_THRESHOLD = 0.70
