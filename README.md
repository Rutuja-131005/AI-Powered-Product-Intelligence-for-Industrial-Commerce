# ProdIntellix: AI-Powered Industrial Product Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com/)
[![Schema Compliance](https://img.shields.io/badge/Contract-252_Columns-brightgreen.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-241_Products_Loaded-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

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

Maps verified product intelligence into the required **252-column schema** and generates a structured Excel/CSV deliverable.

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

| Input             | Purpose                          |
| ----------------- | -------------------------------- |
| Part Number / SKU | Individual product research      |
| Product Image     | Nameplate/product identification |
| Technical PDF     | Specification extraction         |
| CSV               | Bulk catalog enrichment          |
| XLSX              | Bulk catalog enrichment          |
| Google Sheet      | Catalog synchronization          |

---

# 📚 RAG & Evidence Grounding

ProdIntellix uses **Chroma Cloud Hybrid RAG** to retrieve relevant product information.

The document pipeline is:

```text
PDF / Web Content
       ↓
Text Extraction
       ↓
Line-Based Chunking
       ↓
Embeddings
       ↓
Chroma Cloud
       ↓
Semantic Retrieval
       ↓
LLM
       ↓
Grounded Product Intelligence
```

Each retrieved document chunk can retain source information such as:

* Document ID
* Chunk index
* Source URL
* Product identifier
* Document reference

This allows generated information to be traced back to supporting evidence.

---

# ⚙️ Product Attribute Intelligence

ProdIntellix extracts up to **50 structured attribute triplets**:

```text
Attribute Name
      +
Attribute Value
      +
Unit of Measure
```

Example:

```text
Voltage     → 480 → VAC
Current     → 40  → A
Weight      → 95  → lb
Interrupt   → 65  → kA
```

Values are normalized to maintain consistency across different sources.

---

# 📝 AI Commerce Enrichment

The platform generates multiple forms of product content:

* Mobile Description
* Invoice Description
* Short Description
* Long Description
* Retail Description
* Marketing Description
* 20 Structured Feature Bullets
* Applications
* Compatibility information
* Product specifications

Generated content is based on retrieved and validated product information.

---

# 🔐 Multi-Source Validation

ProdIntellix compares information from multiple sources.

```text
Manufacturer
     │
     ├── Voltage: 480 VAC
     │
Distributor
     │
     ├── Voltage: 480 VAC
     │
Datasheet
     │
     └── Voltage: 480 VAC
              ↓
       Source Consensus
              ↓
         VERIFIED
```

When conflicting information is detected:

```text
Manufacturer → 95 lb
Distributor  → 94 lb
              ↓
       Conflict Detected
              ↓
        Review Required
```

This helps reduce unsupported or hallucinated product specifications.

---

# 📊 Enterprise Output

ProdIntellix generates:

### Sheet 1 — Product Details

A strict **252-column contractual schema** containing the enriched product information.

### Sheet 2 — Search Links

Contains discovered authoritative URLs and references used during product research.

Final output:

```text
ProdIntellix_Output.xlsx
```

The platform can also generate CSV output.

---

# 🛠️ Technology Stack

| Layer                   | Technology                                |
| ----------------------- | ----------------------------------------- |
| Frontend                | HTML5, Modern CSS, JavaScript             |
| Backend                 | Python, FastAPI                           |
| Vector Database         | Chroma Cloud                              |
| Embeddings              | Hugging Face / `all-MiniLM-L6-v2`         |
| LLM                     | OpenRouter / LLaMA 3.3 70B, Google Gemini |
| PDF Processing          | pypdf                                     |
| Word Processing         | python-docx                               |
| Data Processing         | pandas                                    |
| Excel Generation        | openpyxl                                  |
| Structured Database     | SQLite / SQLAlchemy                       |
| Spreadsheet Integration | Google Sheets + Apps Script               |
| Deployment              | Vercel / Uvicorn                          |

---

# 📁 Project Structure

```text
ProdIntellix/
│
├── app.py
├── config.py
├── ingest.py
├── rag.py
├── history.py
├── requirements.txt
├── .env.example
│
├── product/
│   ├── identity.py
│   ├── extractor.py
│   ├── normalizer.py
│   ├── validator.py
│   ├── confidence.py
│   ├── prompts.py
│   └── schema.py
│
├── sources/
│   ├── search.py
│   ├── scraper.py
│   ├── fetcher.py
│   └── source_ranker.py
│
├── export/
│   ├── output_schema.py
│   ├── mapper.py
│   └── exporter.py
│
├── services/
│   ├── product_pipeline.py
│   └── google_sheet_service.py
│
├── db/
│   ├── database.py
│   └── models.py
│
├── jobs/
│   └── processor.py
│
├── templates/
├── static/
├── tests/
└── docs/
```

# ▶️ Run Locally

Start the FastAPI server:

```bash
python app.py
```

Open:

**[http://localhost:8000](http://localhost:8000)**

---

# 🎯 Demo Workflow

### Individual Product

1. Open the ProdIntellix dashboard.
2. Enter a part number, SKU, or product information.
3. Start product research.
4. ProdIntellix resolves the product identity.
5. Multiple sources are discovered and ranked.
6. Relevant documents are retrieved through RAG.
7. AI extracts and normalizes specifications.
8. Sources are cross-validated.
9. Product descriptions and features are generated.
10. View the enriched product dashboard.
11. Generate the final Excel/CSV output.

### Bulk Catalog

```text
CSV/XLSX
   ↓
Upload Catalog
   ↓
Process Products
   ↓
Multi-Source Research
   ↓
RAG + AI Enrichment
   ↓
Validation
   ↓
252-Column Mapping
   ↓
ProdIntellix_Output.xlsx
```

---

# 📤 Output Example

The generated workbook contains:

```text
ProdIntellix_Output.xlsx
│
├── Product Details
│   ├── Product Identity
│   ├── Taxonomy
│   ├── Descriptions
│   ├── Features
│   ├── Attributes
│   ├── Technical Specifications
│   └── Commerce Information
│
└── Search Links
    ├── Manufacturer URLs
    ├── Distributor URLs
    ├── PDF References
    └── Other Sources
```

---

# 🔍 Example Product Research

Example input:

```text
Part Number: 140U-J0D3-C40
Brand: Allen-Bradley
```

ProdIntellix:

```text
Input
  ↓
Identity Resolution
  ↓
Source Discovery
  ↓
Manufacturer / Distributor / PDF Research
  ↓
Chroma RAG
  ↓
AI Extraction
  ↓
Validation
  ↓
Commercial Enrichment
  ↓
252-Column Output
```

---

# 🌟 Why ProdIntellix?

Traditional product catalog enrichment requires manually researching hundreds of attributes across multiple sources.

ProdIntellix automates this process by combining:

**Multi-source research + RAG + AI extraction + normalization + validation + commerce enrichment + structured export**

into a single workflow.

---

# 🔮 Future Scope

* Knowledge graph-based product relationships
* Advanced vision-language product analysis
* Automated technical table extraction
* More industrial source connectors
* Human-in-the-loop active learning
* Large-scale asynchronous catalog processing
* Advanced product similarity and recommendation
* Automated catalog quality scoring
