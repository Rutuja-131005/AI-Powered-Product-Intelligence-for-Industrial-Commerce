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
IS_VERCEL = os.getenv("VERCEL") == "1" or bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

if IS_VERCEL:
    DATA_DIR = Path("/tmp/data")
    CHROMA_DIR = Path("/tmp/chroma_db")
else:
    DATA_DIR = BASE_DIR / "data"
    CHROMA_DIR = BASE_DIR / "chroma_db"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'catalog.db'}")

# Chroma Cloud Configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "api.trychroma.com")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "8092f213-aef2-4d28-b9c8-ec7c84e7ad0d")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "Product-Intelligence")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "Product_Intelligence_Catalog")

# AI / Model Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Batch Processing & Rate Limits
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "10"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

# Confidence Thresholds
CONFIDENCE_HIGH_THRESHOLD = 0.85
CONFIDENCE_MEDIUM_THRESHOLD = 0.70

# Razorpay Payment & Risk Configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key_prodintellix")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "mock_secret_prodintellix")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "mock_webhook_secret")
HSN_GST_MASTER_PATH = DATA_DIR / "hsn_gst_master.csv"

