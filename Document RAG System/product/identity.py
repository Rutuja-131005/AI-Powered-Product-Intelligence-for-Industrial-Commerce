"""
Product Identity Resolution Module
Computes canonical identity keys, brand consensus, and normalized part numbers.
"""

import re
from typing import Dict, Any, Tuple, Optional

BRAND_ALIASES = {
    "ab": "Allen-Bradley",
    "allen bradley": "Allen-Bradley",
    "allen-bradley": "Allen-Bradley",
    "rockwell": "Allen-Bradley",
    "rockwell automation": "Allen-Bradley",
    
    "square d": "Square D",
    "squared": "Square D",
    "schneider": "Schneider Electric",
    "schneider electric": "Schneider Electric",
    
    "siemens": "Siemens",
    "siemens ag": "Siemens",
    
    "eaton": "Eaton",
    "cutler hammer": "Eaton",
    "cutler-hammer": "Eaton",
    "bussmann": "Eaton Bussmann",
    
    "abb": "ABB",
    "baldor": "ABB Baldor",
    
    "honeywell": "Honeywell",
    "parker": "Parker Hannifin",
    "parker hannifin": "Parker Hannifin"
}

def resolve_product_identity(
    mfg_part_num: Optional[str],
    part_desc: Optional[str],
    e1_brand: Optional[str],
    unilog_brand: Optional[str],
    dib_brand: Optional[str],
    part_manuf: Optional[str]
) -> Dict[str, Any]:
    """
    Computes canonical identity keys, normalized part numbers, and resolved brand.
    """
    raw_pn = str(mfg_part_num or "").strip()
    if raw_pn.lower() in ["nan", "none", "null"]:
        raw_pn = ""

    # Clean whitespace and normalize part number
    canonical_pn = re.sub(r'\s+', ' ', raw_pn).upper()
    normalized_pn = re.sub(r'[^A-Za-z0-9]', '', canonical_pn).upper()

    # Brand Candidates with Priority: Part_Manuf (0.40) > Unilog (0.30) > E1 (0.20) > DIB (0.10)
    candidates = []
    if part_manuf and str(part_manuf).strip().lower() not in ["nan", "none", "null", ""]:
        candidates.append((str(part_manuf).strip(), 0.40))
    if unilog_brand and str(unilog_brand).strip().lower() not in ["nan", "none", "null", ""]:
        candidates.append((str(unilog_brand).strip(), 0.30))
    if e1_brand and str(e1_brand).strip().lower() not in ["nan", "none", "null", ""]:
        candidates.append((str(e1_brand).strip(), 0.20))
    if dib_brand and str(dib_brand).strip().lower() not in ["nan", "none", "null", ""]:
        candidates.append((str(dib_brand).strip(), 0.10))

    if not candidates and part_desc:
        desc_lower = str(part_desc).lower()
        for alias, canonical in BRAND_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', desc_lower):
                candidates.append((canonical, 0.70))
                break

    if not candidates:
        resolved_brand = "Unknown Manufacturer"
        brand_confidence = 0.40
    else:
        score_map: Dict[str, float] = {}
        for raw_name, weight in candidates:
            cleaned = raw_name.strip()
            canonical = BRAND_ALIASES.get(cleaned.lower(), cleaned.title())
            score_map[canonical] = score_map.get(canonical, 0.0) + weight

        sorted_brands = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        resolved_brand, raw_score = sorted_brands[0]
        brand_confidence = min(0.99, max(0.70, raw_score + 0.35))

    # Canonical identity key
    canonical_key = f"{normalized_pn}_{re.sub(r'[^A-Za-z0-9]', '', resolved_brand).upper()}"

    return {
        "Canonical_Key": canonical_key,
        "Canonical_Part_Number": canonical_pn,
        "Normalized_Part_Number": normalized_pn,
        "Resolved_Brand": resolved_brand,
        "Identity_Confidence": brand_confidence
    }
