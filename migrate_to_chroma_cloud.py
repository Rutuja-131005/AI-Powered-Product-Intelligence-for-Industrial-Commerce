"""
Chroma Cloud Migration Script
Migrates and embeds catalog products and documents from local storage/dataset into Chroma Cloud.
"""

import os
import csv
import sys
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from chroma_cloud_client import (
    get_chroma_client,
    get_or_create_collection,
    chunk_text_line_based,
    CHROMA_HOST,
    CHROMA_TENANT,
    CHROMA_DATABASE,
    CHROMA_API_KEY
)

def run_migration(csv_path: str = "dataset.csv", batch_size: int = 50):
    logger.info("==================================================")
    logger.info("    PRODINTELLIX — CHROMA CLOUD MIGRATION         ")
    logger.info("==================================================")
    logger.info(f"Target Chroma Host:     {CHROMA_HOST}")
    logger.info(f"Target Tenant ID:       {CHROMA_TENANT}")
    logger.info(f"Target Database:        {CHROMA_DATABASE}")
    logger.info(f"API Key Configured:     {'YES (Cloud Mode)' if CHROMA_API_KEY else 'NO (Local Fallback)'}")
    logger.info("--------------------------------------------------")

    if not os.path.exists(csv_path):
        alt = os.path.join("data", os.path.basename(csv_path))
        if os.path.exists(alt):
            csv_path = alt
        else:
            logger.error(f"Cannot find dataset at {csv_path}")
            return

    # Initialize collection
    collection = get_or_create_collection("Product_Intelligence_Catalog")
    logger.info(f"Connected to collection: {collection.name}")

    # Read records from CSV
    records = []
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    logger.info(f"Loaded {len(records)} product records from {csv_path}")

    # Prepare batches
    documents = []
    metadatas = []
    ids = []

    for idx, row in enumerate(records):
        pn = row.get("Mfg_Part_Num") or row.get("PART_NUMBER") or f"PART-{idx+1}"
        desc = row.get("Part_Desc") or row.get("SHORT_DESC") or "Industrial Hardware Component"
        brand = row.get("E1_Brand") or row.get("BRAND_NAME") or row.get("Unilog_Brand") or "Industrial Brand"
        mfg = row.get("Part_Manuf") or row.get("MANUFACTURER_NAME") or f"{brand} Manufacturing"

        full_text = f"Part Number: {pn}\nBrand: {brand}\nManufacturer: {mfg}\nDescription: {desc}\n"
        for k, v in row.items():
            if k not in ["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "Part_Manuf"] and v:
                full_text += f"{k}: {v}\n"

        chunks = chunk_text_line_based(full_text, max_chunk_size=1000)
        for c_idx, chunk in enumerate(chunks):
            doc_id = f"doc-{pn}-{c_idx+1}"
            documents.append(chunk)
            metadatas.append({
                "source_doc_id": pn,
                "chunk_index": c_idx,
                "part_number": pn,
                "brand": brand,
                "manufacturer": mfg,
                "source": "dataset.csv"
            })
            ids.append(doc_id)

    logger.info(f"Generated {len(documents)} chunks from {len(records)} products. Uploading to Chroma in batches...")

    # Upload in batches
    total = len(documents)
    for i in range(0, total, batch_size):
        b_docs = documents[i : i + batch_size]
        b_meta = metadatas[i : i + batch_size]
        b_ids = ids[i : i + batch_size]

        try:
            collection.upsert(
                documents=b_docs,
                metadatas=b_meta,
                ids=b_ids
            )
            logger.info(f"Progress: {min(i + batch_size, total)} / {total} chunks embedded & upserted.")
        except Exception as e:
            logger.error(f"Error uploading batch {i}: {e}")

    count = collection.count()
    logger.info("==================================================")
    logger.info(f"Migration Complete! Total items in Chroma collection: {count}")
    logger.info("==================================================")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "dataset.csv"
    run_migration(csv_file)
