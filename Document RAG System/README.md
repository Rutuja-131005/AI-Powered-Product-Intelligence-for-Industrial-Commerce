# AI-Powered Product Intelligence for Industrial Commerce

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com/)
[![Schema Compliance](https://img.shields.io/badge/Contract-252_Columns-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An enterprise-grade **AI-Powered Product Intelligence Platform** built for industrial distributor and manufacturer catalogs. It extends a local **Document RAG System** (ChromaDB + SentenceTransformers + Google Gemini) to convert sparse, inconsistent 6-column product inputs into structured, enriched, validated, traceable, and commerce-ready catalog data conforming strictly to the **252-column contractual output schema**.

---

## 🌟 Key Capabilities

1. **Deterministic 252-Column Output Contract:**
   - Exact static header sequence preserved across all 252 commerce fields.
   - 100% preservation of raw source columns (`Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`).
   - Populates up to **50 Attribute Triplets** (`ATTR_NAME_1..50`, `ATTR_VALUE_1..50`, `ATTR_UOM_1..50`) normalized to ANSI/NIST standards (`IN`, `MM`, `LBS`, `V`, `VAC`, `VDC`, `A`, `HP`, `KW`, `PSI`, `°C`, etc.).
2. **Multi-Source Identity Resolution:**
   - Weighted consensus algorithm resolving canonical manufacturer and brand aliases (e.g. Rockwell/Allen-Bradley, Square D/Schneider Electric, Siemens, Eaton, ABB, Honeywell, Parker).
   - Generates canonical and alphanumeric normalized part numbers for cross-catalog search.
3. **Evidence-Grounded Copy Generation:**
   - Generates commerce titles, descriptions (`MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`), and **20 Feature Bullets** (`ITEM_FEATURES_1`..`20`) strictly grounded in extracted facts without hallucinating unverified technical specs.
4. **Source Discovery & Digital Asset Matching:**
   - Discovers official manufacturer portals, datasheets, user manuals, 3D CAD drawings, SDS/MSDS links, and authorized distributor listings.
5. **Relational Database Architecture (SQLite / PostgreSQL):**
   - 8 normalized relational tables: `jobs`, `products`, `product_attributes`, `sources`, `evidence`, `validation_results`, `reviews`, `product_assets`.
6. **Failure Isolation & Scaling:**
   - Per-row isolation ensures single product anomalies never fail the overall batch job.
   - Built-in identity caching and retry handling.
7. **Interactive Web Studio & Reviewer Queue:**
   - Modern dark-mode interface with live batch telemetry, KPI dashboards, deep-dive modal inspector (with 4 sub-views: Specs, 50 Triplets, Evidence Trail, Raw Inputs), human review queue (`APPROVE`, `EDIT`, `REJECT`), and 1-click CSV/XLSX downloads.

---

## 🏗️ End-to-End Architecture

```text
[Sparse CSV / XLSX Upload]
           │
           ▼
[1. Input Schema Validation] ──────► (Invalid? Reject with error report)
           │
           ▼
[2. Enrichment Job Manager]
           │
           ▼ (Per-Row Isolated Processing)
[3. Identity Resolution] (Brand Consensus + Canonical PN)
           │
           ▼
[4. Cache Check] ──────────────────► (Hit? Reuse normalized identity)
           │
           ▼
[5. Source Discovery] (Manufacturer Portals + Datasheets + CAD + SDS)
           │
           ▼
[6. Product RAG Grounding] (ChromaDB semantic retrieval)
           │
           ▼
[7. Fact & Spec Extraction] (Electrical, Mechanical, Physical Dimensions)
           │
           ▼
[8. Unit & Attribute Normalization] (ANSI/NIST standard UOMs)
           │
           ▼
[9. Commerce Copy Synthesis] (Titles, Descriptions, 20 Feature Bullets)
           │
           ▼
[10. Validation & Provenance Scoring] ───► (Low score / conflict? Review Queue)
           │
           ▼
[11. 252-Column Schema Mapping]
           │
           ▼
[12. Relational DB Persistence]
           │
           ▼
[13. Exact 252-Column CSV / XLSX Export Engine]
```

---

## 📊 252-Column Header Contract

| Group | Columns | Count | Description |
| :--- | :--- | :---: | :--- |
| **Group 1** | 1–6 | 6 | `Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf` |
| **Group 2** | 7–23 | 17 | Core Identifiers & Taxonomy (`PRODUCT_NAME`, `MANUFACTURER`, `BRAND_NAME`, `CANONICAL_PART_NUMBER`, `NORMALIZED_PART_NUMBER`, `PRIMARY_CATEGORY`..`EAN`) |
| **Group 3** | 24–29 | 6 | Descriptions (`MOBILE_DESC`, `INVOICE_DESC`, `SHORT_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`) |
| **Group 4** | 30–49 | 20 | Feature Bullets (`ITEM_FEATURES_1` through `ITEM_FEATURES_20`) |
| **Group 5** | 50–55 | 6 | Commerce Metadata (`WITH`, `APPROVALS_STANDARDS`, `APPLICATION`, `INCLUDES`, `SEARCH_KEYWORDS`, `SEO_TITLE`) |
| **Group 6** | 56–205 | 150 | 50 Attribute Triplets (`ATTR_NAME_1..50`, `ATTR_VALUE_1..50`, `ATTR_UOM_1..50`) |
| **Group 7** | 206–224 | 19 | Physical, Packaging & Dimensions (`WEIGHT`, `LENGTH`, `WIDTH`, `HEIGHT`, `PACKAGE_QTY`, `WARRANTY_YEARS`, `NEMA_RATING`, `IP_RATING`...) |
| **Group 8** | 225–249 | 25 | Digital Assets & Technical Ratings (`PRIMARY_IMAGE_URL`, `SPEC_SHEET_URL`, `USER_MANUAL_URL`, `CAD_DRAWING_URL`, `VOLTAGE_RATING`, `CURRENT_RATING`...) |
| **Group 9** | 250–252 | 3 | Flags (`COUNTRY_OF_ORIGIN`, `DISCONTINUED_STATUS`, `IMAGE_FLAG`) |
| **Total** | **1–252** | **252** | **Strict, fixed contractual headers in exact order** |

---

## 📡 REST API Reference

- `POST /api/jobs` — Ingest CSV/XLSX file, validate schema, start enrichment.
- `GET /api/jobs/{job_id}` — Real-time progress %, row counts, and KPIs.
- `POST /api/jobs/{job_id}/start` — Resume/trigger batch processing.
- `GET /api/jobs/{job_id}/products` — Paginated, searchable, brand/status filterable catalog.
- `GET /api/products/{product_id}` — Canonical product inspection with full JSON payload.
- `POST /api/products/{product_id}/reprocess` — Re-run enrichment for a specific product.
- `GET /api/review-queue` — List products flagged for human review (`NEEDS_REVIEW`, `PARTIAL`).
- `POST /api/products/{product_id}/review` — Submit human review action (`APPROVE`, `EDIT`, `REJECT`).
- `GET /api/products/{product_id}/sources` — Discovered authoritative and reference URLs.
- `GET /api/products/{product_id}/evidence` — Grounded ChromaDB RAG chunk citations.
- `GET /api/jobs/{job_id}/export/csv` — Download strict 252-column CSV.
- `GET /api/jobs/{job_id}/export/xlsx` — Download strict 252-column XLSX workbook.
- `POST /upload`, `POST /query`, `GET /files`, `GET /status`, `GET /history` — Preserved Document RAG endpoints.

---

## 🧪 Automated Test Suite

```bash
# Run all tests
python tests/test_252_schema.py
python tests/test_identity.py
python tests/test_workflow.py
python tests/test_api_endpoints.py
python tests/test_synthetic_product.py
```
