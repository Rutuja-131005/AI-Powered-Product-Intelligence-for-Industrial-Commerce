# ProdIntellix: AI-Powered Industrial Product Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com/)
[![Schema Compliance](https://img.shields.io/badge/Contract-252_Columns-brightgreen.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-241_Products_Loaded-success.svg)]()
---

# 🌐 ProdIntellix

> **AI-Powered Product Intelligence, Multi-Source Verification & 252-Column Enrichment Engine for Industrial Commerce.**

ProdIntellix transforms sparse and incomplete industrial product information into **enriched, validated, traceable, and commerce-ready product intelligence** using multi-source research, hybrid RAG, AI extraction, cross-source validation, and automated catalog generation.

---

## 🚀 Overview

Industrial product information is often scattered across manufacturer websites, distributor portals, technical PDFs, manuals, catalogs, and product images.

**ProdIntellix** brings these sources together and converts minimal product information into structured product intelligence.

Given a **part number, product description, brand, manufacturer, image/nameplate, PDF, or catalog**, the platform can:

* Identify the canonical product and brand
* Discover authoritative product sources
* Retrieve relevant technical evidence using RAG
* Extract and normalize technical specifications
* Cross-validate information across multiple sources
* Detect specification conflicts
* Generate commerce-ready descriptions and features
* Produce the required **252-column product output**
* Export the final catalog as Excel/CSV
* Synchronize product information with Google Sheets

---

# 🔄 End-to-End Workflow

```text
┌─────────────────────────────┐
│       MULTIMODAL INPUT      │
│                             │
│ Part Number / SKU           │
│ Product Image / Nameplate   │
│ PDF / Manual                │
│ CSV / XLSX Catalog          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│   PRODUCT IDENTITY          │
│                             │
│ MPN + Brand + Manufacturer  │
│ Identity Resolution         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ MULTI-SOURCE DISCOVERY      │
│                             │
│ Manufacturer Websites       │
│ Distributors                │
│ Datasheets / Manuals        │
│ Catalogs / Technical Docs   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│   CHROMA CLOUD HYBRID RAG   │
│                             │
│ Chunking → Embeddings       │
│ Semantic Retrieval          │
│ Evidence Grounding          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ AI EXTRACTION & NORMALIZE   │
│                             │
│ 50 Attribute Triplets       │
│ Value + UOM Normalization   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ CROSS-SOURCE VALIDATION     │
│                             │
│ Consensus Detection         │
│ Conflict Arbitration        │
│ Confidence Scoring          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ COMMERCIAL AI ENRICHMENT     │
│                             │
│ Descriptions                │
│ 20 Feature Bullets          │
│ Applications & Compatibility│
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│    252-COLUMN OUTPUT        │
│                             │
│ Product Details             │
│ Search Links                │
│ Evidence & References       │
└──────────────┬──────────────┘
               ↓
       XLSX / CSV / Sheets
```

---

# ✨ Key Features

### 🔎 1. Multi-Source Product Research
Researches manufacturer websites, industrial distributors, technical PDFs, catalogs, manuals, and other authoritative sources.

### 🧠 2. AI-Powered RAG Enrichment
Uses Chroma Cloud and LLMs to retrieve relevant evidence and extract grounded product information.

### ✅ 3. Product Identity & Validation
Resolves product and brand identity, compares information across sources, detects conflicts, and calculates confidence.

### ⚙️ 4. Smart Attribute Extraction
Extracts up to **50 technical attribute triplets** with normalized values and units of measurement.

### 🛒 5. Commerce-Ready Content
Generates mobile, invoice, short, long, retail, and marketing descriptions along with **20 structured product features**.

### 📊 6. 252-Column Contractual Output
Maps verified product intelligence into the required **252-column schema** and generates a structured Excel/CSV deliverable (`ProdIntellix_Output.xlsx`).

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Product Input     │
                    │ CSV / XLSX / Image  │
                    │ PDF / Part Number   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Identity Resolution │
                    └──────────┬──────────┘
                               ↓
              ┌────────────────┴────────────────┐
              ↓                                 ↓
    ┌──────────────────┐              ┌──────────────────┐
    │ Web Search       │              │ Document Input   │
    │ Manufacturer     │              │ PDF / Manual     │
    │ Distributor      │              │ Catalog          │
    └────────┬─────────┘              └────────┬─────────┘
             └────────────────┬────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │  Chroma Cloud RAG   │
                    │ Vector Retrieval    │
                    │ Evidence Grounding  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Gemini / OpenRouter │
                    │ AI Extraction       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Validation Engine   │
                    │ Consensus / Conflict│
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Enrichment Engine   │
                    │ Descriptions/Specs  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ 252-Column Mapper   │
                    └──────────┬──────────┘
                               ↓
                  ┌────────────┴────────────┐
                  ↓                         ↓
             XLSX / CSV              Google Sheets
```

---

# 🧩 Multimodal Input

ProdIntellix supports multiple ways to provide product information:

| Input | Purpose |
| :--- | :--- |
| **Part Number / SKU** | Individual product deep research |
| **Product Image / Nameplate** | Visual OCR, model extraction, and web discovery |
| **Technical PDF / Datasheet** | Table parsing, spec extraction & RAG indexing |
| **CSV / XLSX File** | 1,000-row batch catalog enrichment |
| **Google Sheets** | Real-time bi-directional catalog sync |

---

# 📚 RAG & Evidence Grounding

ProdIntellix uses **Chroma Cloud Hybrid RAG** to retrieve relevant product information.

The document pipeline is:

```text
PDF / Web Content
       ↓
Text Extraction
       ↓
Line-Based Chunking (<16 KiB)
       ↓
Embeddings (MiniLM / Qwen)
       ↓
Chroma Cloud
       ↓
Semantic Retrieval & RRF
       ↓
LLM Grounding
       ↓
Verified Product Intelligence
```

Each retrieved document chunk retains complete provenance:
* Document ID
* Chunk index
* Source URL / Portal
* Product identifier
* Document reference

---

# ⚙️ Product Attribute Intelligence

ProdIntellix extracts up to **50 structured attribute triplets**:

```text
Attribute Name + Attribute Value + Unit of Measure (UOM)
```

Example:
```text
Voltage     → 480 → VAC
Current     → 40  → A
Weight      → 95  → lb
Interrupt   → 65  → kA
```

Values are normalized to ANSI/NIST standards to maintain consistency across different sources.

---

# 📝 AI Commerce Enrichment

The platform automatically generates commerce-grade copy:

* **Mobile Description**
* **Invoice Description**
* **Short Description**
* **Long Technical Description**
* **Retail Description**
* **Marketing Description**
* **20 Structured Feature Bullets**
* **Target Applications & Compatibility Matrix**

---

# 🔐 Multi-Source Validation & Conflict Resolution

ProdIntellix compares information across 3+ independent sources:

```text
Manufacturer Portal  ─── Voltage: 480 VAC
Distributor Catalog  ─── Voltage: 480 VAC   ──► Consensus: VERIFIED (97% Confidence)
Datasheet PDF        ─── Voltage: 480 VAC
```

When conflicting information is detected:

```text
Manufacturer Portal  ─── Weight: 95 lb (Authoritative)
Distributor Catalog  ─── Weight: 94 lb (Distributor Estimate)
                               ↓
                   Conflict Detected & Arbitrated
```

---

# 📊 Enterprise Output (`ProdIntellix_Output.xlsx`)

ProdIntellix generates a dual-sheet Excel deliverable:

* **Sheet 1 — `Product Details`**: Strict **252-column contractual schema** containing enriched attributes, classifications, taxonomy, and commerce copy.
* **Sheet 2 — `Search Links`**: All discovered authoritative URLs (Manufacturer, Distributors, Datasheets, Manuals, CAD, and SDS).

---

# 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, Modern CSS, JavaScript |
| **Backend** | Python, FastAPI |
| **Vector Database** | Chroma Cloud (`api.trychroma.com`) |
| **Embeddings** | Hugging Face / `all-MiniLM-L6-v2` |
| **LLMs** | OpenRouter (LLaMA 3.3 70B), Google Gemini |
| **PDF Processing** | `pypdf`, `python-docx` |
| **Data Processing** | `pandas`, `openpyxl` |
| **Database** | SQLite / SQLAlchemy |
| **Spreadsheet Integration** | Google Sheets + Apps Script |
| **Deployment** | Vercel (`@vercel/python`) / Uvicorn |

---

# 📁 Project Structure

```text
ProdIntellix/
│
├── app.py                      # FastAPI Main Server & Endpoints
├── config.py                   # Centralized Configuration & Environment
├── ingest.py                   # Document Chunking & Ingestion
├── rag.py                      # Chroma Retrieval & Query Engine
├── chroma_cloud_client.py      # Chroma Cloud Client & Line Chunking
├── migrate_to_chroma_cloud.py  # Chroma Cloud Catalog Batch Ingestion
├── history.py                  # Research Query Persistence
├── requirements.txt            # Python Dependencies
├── vercel.json                 # Vercel Deployment Configuration
├── .env.example                # Environment Variables Template
│
├── product/
│   ├── identity.py             # Brand & Part Number Disambiguation
│   ├── extractor.py            # Technical Spec & Attribute Extractor
│   ├── normalizer.py           # ANSI/NIST Unit Normalization
│   ├── validator.py            # Multi-Source Consensus & Conflict Engine
│   ├── confidence.py           # Calibrated Confidence Scoring
│   ├── enricher.py             # 20 Feature Bullets & Descriptions
│   ├── prompts.py              # LLM System Prompts
│   └── schema.py               # Output Schema Definitions
│
├── sources/
│   ├── search.py               # Multi-Source Discovery
│   ├── scraper.py              # Web Content Parsing
│   ├── fetcher.py              # Async HTTP Fetching
│   ├── source_ranker.py        # Authority & Domain Weighting
│   └── research_service.py     # End-to-End Product Research Service
│
├── export/
│   ├── output_schema.py        # Strict 252 Column Schema Contract
│   ├── mapper.py               # 252-Column Field Mapper
│   └── exporter.py             # Dual-Sheet Excel & CSV Exporter
│
├── services/
│   ├── product_pipeline.py     # Core Enrichment Pipeline
│   └── google_sheet_service.py # Google Sheets Cloud Sync
│
├── db/
│   ├── database.py             # SQLAlchemy Engine
│   └── models.py               # Job & Product Table Models
│
├── jobs/
│   └── processor.py            # Async Batch Job Processor
│
├── templates/
│   └── index.html              # Modern Web Application UI
├── static/
│   ├── style.css               # Clean Design System & Themes
│   ├── script.js               # Dynamic Dashboard & Interactive Handlers
│   └── logo.png                # Circular Brand Logo
└── tests/
    └── test_252_schema.py      # Contract Compliance Test Suite
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Rutuja-131005/AI-Powered-Product-Intelligence-for-Industrial-Commerce.git
cd AI-Powered-Product-Intelligence-for-Industrial-Commerce
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure environment variables

Create a `.env` file from the template:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=8092f213-aef2-4d28-b9c8-ec7c84e7ad0d
CHROMA_DATABASE=Product-Intelligence
CHROMA_HOST=api.trychroma.com
```

---

# ▶️ Run Locally

Start the FastAPI server:

```bash
python app.py
```

Open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

---

# 🎯 Demo Walkthrough

1. Open **[http://localhost:8000](http://localhost:8000)**.
2. Click any **Quick Reference Topic** (e.g., `⚡ Allen-Bradley 140U-J0D3-C40` or `⚡ Dewalt DCF860B`).
3. Click **"RESEARCH WEBSITES"** to watch multi-source discovery, RAG evidence grounding, and specification extraction.
4. Click **"VIEW PRODUCT DASHBOARD"** to see the live dynamic dashboard (consensus validation, conflict arbitration, 20 features, and commercial copy).
5. Click **"GENERATE OUTPUT (ProdIntellix_Output.xlsx)"** to download the completed 2-sheet Excel catalog.

---

# 👥 Team

**ProdIntellix**  
AI-Powered Product Intelligence for Industrial Commerce  
*Built for the Industrial Commerce Product Intelligence Hackathon.*
