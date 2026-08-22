# ProdIntellix: AI-Powered Industrial Product Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com/)
[![Schema Compliance](https://img.shields.io/badge/Contract-252_Columns-brightgreen.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-241_Products_Loaded-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**ProdIntellix** is an enterprise-grade **AI-Powered Product Intelligence and Catalog Enrichment Platform** purpose-built for industrial distributors, wholesalers, and manufacturers. It transforms sparse, inconsistent, 6-column product inputs into complete, normalized, authoritative, and commerce-ready catalog records conforming strictly to the **contractual 252-column output schema**.

---

## 🌟 Key Features

1. **Dynamic Dataset Loading via `csv.DictReader`:**
   - No hardcoded Python datasets or static arrays.
   - Dynamically loads and parses catalog records directly from `dataset.csv` using native `csv.DictReader`.
   - Supports 241+ real industrial products across leading brands (Diablo, 3M, Milwaukee, Mirka, GE, Trex, TimberTech, Kichler, Leviton, Philips, Dewalt, Makita, Festool, Senco, Hunter, etc.).

2. **Deterministic 252-Column Output Contract:**
   - 100% preservation of raw source columns (`Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`).
   - Populates up to **50 Attribute Triplets** (`ATTR_NAME_1..50`, `ATTR_VALUE_1..50`, `ATTR_UOM_1..50`) with ANSI/NIST normalized units (`IN`, `MM`, `LBS`, `V`, `VAC`, `VDC`, `A`, `HP`, `KW`, `PSI`, `°C`, etc.).
   - Exports directly to 252-column CSV and Excel XLSX formats.

3. **Multi-Source Identity Resolution & Disambiguation:**
   - Weighted consensus algorithm resolving brand aliases (e.g. Rockwell/Allen-Bradley, Square D/Schneider Electric, Siemens, Eaton, ABB, Honeywell, Parker, Kichler, Leviton).
   - Generates canonical and normalized alphanumeric part numbers for cross-catalog deduplication.

4. **Multi-Website Research & Source Discovery:**
   - Deep search query synthesis targeting official manufacturer portals, technical datasheets, user manuals, 3D CAD models, and SDS/MSDS compliance files.

5. **Multimodal Ingestion (Images, Technical PDFs, Spreadsheets):**
   - Ingest product images via visual OCR and spec detection.
   - Parse dense technical spec sheets and equipment manuals in PDF format.
   - Batch upload sparse catalog CSV/XLSX spreadsheets.

6. **Conversational Product AI & RAG Grounding:**
   - Semantic retrieval against local ChromaDB vector store powered by SentenceTransformers.
   - Grounded conversational assistant answering technical compatibility and specification queries.

7. **Clean Web Application Interface:**
   - Modern, responsive console interface with live telemetry, multimodal dropzones, instant web research inspector, and database repository management.
   - Secure local export actions (Download 252-Column CSV / XLSX) without exposing raw external spreadsheet URLs.

---

## 📂 Dataset Integration (`dataset.csv`)

The system loads catalog data dynamically using Python's standard `csv.DictReader`:

```python
import csv

# Open and read the dataset dynamically
with open("dataset.csv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Each row is a dictionary containing:
        # row["Mfg_Part_Num"], row["Part_Desc"], row["E1_Brand"],
        # row["Unilog_Brand"], row["DIB_Brand"], row["Part_Manuf"]
        print(row)
```

The dataset includes 241 diverse industrial hardware products across categories:
- Abrasives & Sanding Belts (Diablo, 3M Cubitron, Mirka)
- Power Tool Accessories & Cut-Off Discs (Milwaukee, Dewalt, Makita)
- Commercial Appliances (Speed Queen, GE, Cafe, LG, KitchenAid)
- Building Materials & Decking (Trex, TimberTech, LP SmartSide, JamesHardie)
- Electrical, Wiring & Lighting (Leviton, Satco, Kichler, Philips, Southwire, Square D)
- Safety & Precision Tools (Edge Eyewear, Wera, Festool, Kreg, Vessel, Bow Products)

---

## 🏗️ System Architecture

```text
[Input Sources: dataset.csv / Images / Spec PDFs / Web Search]
                             │
                             ▼
              [1. Input Schema Validation]
                             │
                             ▼
              [2. Identity Resolution Engine]
            (Brand Consensus + Canonical Part Number)
                             │
                             ▼
              [3. Multi-Website Source Discovery]
      (Manufacturer Portals + Datasheets + CAD + SDS)
                             │
                             ▼
              [4. Fact & Spec Extraction Engine]
     (Electrical, Mechanical, Dimensional Attribute Triplets)
                             │
                             ▼
              [5. ANSI/NIST UOM Normalizer]
                             │
                             ▼
              [6. Grounded Commerce Copy Synthesis]
         (Titles, Short/Long Descriptions, 20 Feature Bullets)
                             │
                             ▼
              [7. Validation & Confidence Scoring]
                             │
                             ▼
              [8. Strict 252-Column Mapping Engine]
                             │
                             ▼
           [9. Relational DB Storage & 252 CSV/XLSX Export]
```

---

## 📊 252-Column Header Contract Breakdown

| Group | Columns | Count | Description |
| :--- | :--- | :---: | :--- |
| **Group 1** | 1–6 | 6 | Raw Input Preservation (`Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`) |
| **Group 2** | 7–23 | 17 | Core Identifiers & Taxonomy (`PRODUCT_NAME`, `MANUFACTURER`, `BRAND_NAME`, `CANONICAL_PART_NUMBER`, `NORMALIZED_PART_NUMBER`, `PRIMARY_CATEGORY`..`EAN`) |
| **Group 3** | 24–29 | 6 | Commerce Descriptions (`MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`) |
| **Group 4** | 30–49 | 20 | Item Feature Bullets (`ITEM_FEATURES_1` through `ITEM_FEATURES_20`) |
| **Group 5** | 50–55 | 6 | Commerce Metadata (`WITH`, `APPROVALS_STANDARDS`, `APPLICATION`, `INCLUDES`, `SEARCH_KEYWORDS`, `SEO_TITLE`) |
| **Group 6** | 56–205 | 150 | 50 Attribute Triplets (`ATTR_NAME_1..50`, `ATTR_VALUE_1..50`, `ATTR_UOM_1..50`) |
| **Group 7** | 206–224 | 19 | Physical Dimensions & Packaging (`WEIGHT`, `LENGTH`, `WIDTH`, `HEIGHT`, `PACKAGE_QTY`, `WARRANTY_YEARS`, `NEMA_RATING`...) |
| **Group 8** | 225–249 | 25 | Digital Assets & Technical Ratings (`PRIMARY_IMAGE_URL`, `SPEC_SHEET_URL`, `USER_MANUAL_URL`, `CAD_DRAWING_URL`, `VOLTAGE_RATING`...) |
| **Group 9** | 250–252 | 3 | Operational Flags (`COUNTRY_OF_ORIGIN`, `DISCONTINUED_STATUS`, `IMAGE_FLAG`) |
| **Total** | **1–252** | **252** | **Strict, fixed contractual headers in exact sequence** |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Rutuja-131005/AI-Powered-Product-Intelligence-for-Industrial-Commerce.git
cd AI-Powered-Product-Intelligence-for-Industrial-Commerce

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup (Optional)
Copy `.env.example` to `.env` and supply your API keys if enabling live cloud LLM queries:
```bash
cp .env.example .env
```

### 4. Running the Application

```bash
# Start the FastAPI server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 🧪 Testing & Verification

Run the full automated test suite covering schema compliance, dynamic identity resolution, workflow execution, and 252-column export verification:

```bash
# Run schema and contract validation tests
python tests/test_252_schema.py

# Run identity resolution and brand normalization tests
python tests/test_identity.py

# Run end-to-end workflow execution tests
python tests/test_workflow.py

# Run synthetic novel part test
python tests/test_synthetic_product.py

# Run service pipeline test
python tests/test_pipeline.py
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the main Web Console UI |
| `/api/jobs` | `POST` | Uploads CSV/XLSX, validates schema, starts batch enrichment |
| `/api/jobs/{job_id}` | `GET` | Returns real-time progress %, counts, and KPIs |
| `/api/jobs/{job_id}/products` | `GET` | Paginated, searchable, brand/status filterable catalog |
| `/api/jobs/{job_id}/export/csv` | `GET` | Downloads strict 252-column CSV file |
| `/api/jobs/{job_id}/export/xlsx` | `GET` | Downloads strict 252-column Excel XLSX workbook |
| `/api/intelligence/search-product` | `POST` | Instant multi-website research on part number / query |
| `/api/intelligence/upload-image` | `POST` | Uploads product image for OCR, web research & enrichment |
| `/api/intelligence/upload-pdf` | `POST` | Uploads PDF technical datasheet for spec extraction |
| `/query` | `POST` | Natural language RAG conversational query against catalog |
| `/status` | `GET` | Vector store & server status telemetry |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
