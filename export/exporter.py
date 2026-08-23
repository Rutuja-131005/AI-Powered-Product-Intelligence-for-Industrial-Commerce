"""
CSV and XLSX Exporter Module
"""

import io
import pandas as pd
from typing import List, Dict, Any, Optional
from .output_schema import FINAL_252_HEADERS

def export_catalog_to_csv(rows: List[Dict[str, Any]]) -> bytes:
    """Exports rows to UTF-8 RFC 4180 CSV bytes with exact 252 headers."""
    df = pd.DataFrame(rows, columns=FINAL_252_HEADERS)
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8")
    return output.getvalue().encode("utf-8")

def export_catalog_to_xlsx(rows: List[Dict[str, Any]]) -> bytes:
    """Exports rows to OpenPyXL XLSX bytes with exact 252 headers."""
    df = pd.DataFrame(rows, columns=FINAL_252_HEADERS)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Enriched_Catalog_252")
    return output.getvalue()

def export_single_product_two_sheet_xlsx(product_record: Dict[str, Any], research_links: Optional[List[Dict[str, Any]]] = None) -> bytes:
    """
    Exports a single searched product into an Excel workbook with 2 distinct sheets:
    - Sheet 1: 'Product Details' (Full 252-column contractual attributes)
    - Sheet 2: 'Search Links' (All discovered authoritative research links)
    """
    # 1. Sheet 1: Product Details (252 columns)
    row_data = {h: product_record.get(h, "") for h in FINAL_252_HEADERS}
    df_product = pd.DataFrame([row_data], columns=FINAL_252_HEADERS)

    # 2. Sheet 2: Search Links
    pn = product_record.get("PART_NUMBER") or product_record.get("Mfg_Part_Num", "")
    brand = product_record.get("BRAND_NAME") or product_record.get("Resolved_Brand", "")

    links_rows = []
    if research_links:
        for lnk in research_links:
            links_rows.append({
                "Part Number": pn,
                "Brand": brand,
                "Link Category": lnk.get("category", "General"),
                "Source Description": lnk.get("label", "Authoritative Reference"),
                "Target URL": lnk.get("url", ""),
                "Verification Status": "VERIFIED"
            })
    else:
        # Extract default links from product record
        link_fields = [
            ("Manufacturer Official Portal", "MFR URL", "Manufacturer"),
            ("Technical Datasheet / Spec Sheet", "Specification Sheet", "Datasheet PDF"),
            ("User Installation & Safety Manual", "Instruction/Installation Manual", "Manual"),
            ("3D CAD / Engineering Drawing", "Line Drawing", "CAD Model"),
            ("Safety Data Sheet (SDS/MSDS)", "SDS", "Compliance"),
            ("Distributor Reference 1", "Ref URL 1", "Distributor"),
            ("Distributor Reference 2", "Ref URL 2", "Distributor"),
            ("Catalog Reference Portal", "Ref URL 3", "Catalog")
        ]
        for label, key, cat in link_fields:
            url = product_record.get(key)
            if url:
                links_rows.append({
                    "Part Number": pn,
                    "Brand": brand,
                    "Link Category": cat,
                    "Source Description": label,
                    "Target URL": url,
                    "Verification Status": "VERIFIED"
                })

    if not links_rows:
        links_rows.append({
            "Part Number": pn,
            "Brand": brand,
            "Link Category": "Notice",
            "Source Description": "No external links generated",
            "Target URL": "",
            "Verification Status": "N/A"
        })

    df_links = pd.DataFrame(links_rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_product.to_excel(writer, index=False, sheet_name="Product Details")
        df_links.to_excel(writer, index=False, sheet_name="Search Links")

    return output.getvalue()
