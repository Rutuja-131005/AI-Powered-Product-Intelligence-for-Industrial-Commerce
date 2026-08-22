"""
Identity Resolution and Disambiguation Engine for Industrial Parts
Resolves brand consensus, part number canonicalization, and technical descriptor patterns.
"""

import re
from typing import Dict, Any, Tuple, Optional

# Standard Manufacturer & Brand Normalization Map
BRAND_CANONICAL_MAP = {
    "ab": "Allen-Bradley",
    "allen bradley": "Allen-Bradley",
    "allen-bradley": "Allen-Bradley",
    "rockwell": "Allen-Bradley",
    "rockwell automation": "Allen-Bradley",
    
    "square d": "Square D",
    "squared": "Square D",
    "schneider": "Schneider Electric",
    "schneider electric": "Schneider Electric",
    "telemecanique": "Schneider Electric",
    
    "siemens": "Siemens",
    "siemens ag": "Siemens",
    "siemens energy": "Siemens",
    
    "eaton": "Eaton",
    "cutler hammer": "Eaton",
    "cutler-hammer": "Eaton",
    "bussmann": "Eaton Bussmann",
    
    "abb": "ABB",
    "baldor": "ABB Baldor",
    "baldor reliance": "ABB Baldor",
    "thomas & betts": "ABB Installation Products",
    
    "honeywell": "Honeywell",
    "honeywell sensing": "Honeywell",
    
    "omron": "Omron Automation",
    "omron automation": "Omron Automation",
    
    "parker": "Parker Hannifin",
    "parker hannifin": "Parker Hannifin",
    
    "smc": "SMC Corporation",
    "smc pneumatics": "SMC Corporation",
    
    "festo": "Festo",
    
    "emerson": "Emerson Electric",
    "rosemount": "Emerson Rosemount",
    "asco": "Emerson ASCO",
    
    "turck": "Turck",
    "banner": "Banner Engineering",
    "banner engineering": "Banner Engineering",
    "sick": "SICK Sensor Intelligence",
    "keyence": "Keyence",
    "phoenix contact": "Phoenix Contact",
    "weidmuller": "Weidmuller",
    "wago": "WAGO",
    "fluke": "Fluke",
    "yaskawa": "Yaskawa Electric",
    "mitsubishi": "Mitsubishi Electric"
}

def resolve_brand(
    e1_brand: Optional[str],
    unilog_brand: Optional[str],
    dib_brand: Optional[str],
    part_manuf: Optional[str],
    part_desc: Optional[str] = ""
) -> Tuple[str, float]:
    """
    Resolves the canonical brand name through multi-source consensus, priority weighting,
    and alias normalization. Returns (resolved_brand, confidence_score).
    """
    candidates = []
    
    # Priority weighting: Part_Manuf (0.4) > Unilog (0.3) > E1 (0.2) > DIB (0.1)
    if part_manuf and str(part_manuf).strip().lower() not in ["nan", "none", "", "null"]:
        candidates.append((str(part_manuf).strip(), 0.40))
    if unilog_brand and str(unilog_brand).strip().lower() not in ["nan", "none", "", "null"]:
        candidates.append((str(unilog_brand).strip(), 0.30))
    if e1_brand and str(e1_brand).strip().lower() not in ["nan", "none", "", "null"]:
        candidates.append((str(e1_brand).strip(), 0.20))
    if dib_brand and str(dib_brand).strip().lower() not in ["nan", "none", "", "null"]:
        candidates.append((str(dib_brand).strip(), 0.10))

    if not candidates:
        # Fallback: check if brand name is mentioned in part description
        if part_desc:
            desc_lower = str(part_desc).lower()
            for raw_key, canonical in BRAND_CANONICAL_MAP.items():
                if re.search(r'\b' + re.escape(raw_key) + r'\b', desc_lower):
                    return canonical, 0.70
        return "Unknown Manufacturer", 0.30

    # Aggregate weighted scores per normalized brand
    score_map: Dict[str, float] = {}
    name_display_map: Dict[str, str] = {}

    for raw_name, weight in candidates:
        cleaned = raw_name.strip()
        lookup_key = cleaned.lower()
        canonical = BRAND_CANONICAL_MAP.get(lookup_key, cleaned.title())
        
        score_map[canonical] = score_map.get(canonical, 0.0) + weight
        name_display_map[canonical] = canonical

    # Pick the highest scoring brand
    sorted_brands = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
    best_brand, best_score = sorted_brands[0]
    
    # Normalize score between 0.70 and 0.99
    confidence = min(0.99, max(0.70, best_score + 0.35))
    return best_brand, confidence

def canonicalize_part_number(mfg_part_num: Optional[str]) -> Tuple[str, str]:
    """
    Returns (canonical_part_number, normalized_part_number).
    - canonical: cleaned uppercase part number with standard hyphens/spaces.
    - normalized: strict alphanumeric uppercase string for index/cross-system search.
    """
    if not mfg_part_num or str(mfg_part_num).strip().lower() in ["nan", "none", "", "null"]:
        return "", ""
    
    raw = str(mfg_part_num).strip()
    canonical = re.sub(r'\s+', ' ', raw).upper()
    normalized = re.sub(r'[^A-Za-z0-9]', '', canonical).upper()
    return canonical, normalized

def parse_industrial_descriptor(part_desc: str) -> Dict[str, Any]:
    """
    Parses key technical parameters embedded in industrial short descriptions.
    e.g. '100A 3P 480V CIR BRKR' or 'PHOTO SENSOR RETRO 24VDC NPN 2M'
    """
    if not part_desc or str(part_desc).strip().lower() in ["nan", "none", "", "null"]:
        return {}
        
    desc = str(part_desc).strip()
    features: Dict[str, Any] = {}

    # Extract Current Rating (e.g., 100A, 15 AMP, 30AMP, 0.5A)
    curr_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:A|AMP|AMPS)\b', desc, re.IGNORECASE)
    if curr_match:
        features["Current_Rating"] = curr_match.group(1)
        features["Current_UOM"] = "A"

    # Extract Voltage Rating (e.g., 480V, 120VAC, 24VDC, 600V)
    volt_match = re.search(r'(\d+(?:\.\d+)?)\s*(V|VAC|VDC|KV|VOLT|VOLTS)\b', desc, re.IGNORECASE)
    if volt_match:
        val = volt_match.group(1)
        uom = volt_match.group(2).upper()
        if uom in ["VOLT", "VOLTS"]:
            uom = "V"
        features["Voltage_Rating"] = val
        features["Voltage_UOM"] = uom

    # Extract Number of Poles (e.g., 3P, 2 POLE, 1P, 4-POLE)
    pole_match = re.search(r'(\d+)\s*(?:P|POLE|POLES)\b', desc, re.IGNORECASE)
    if pole_match:
        features["Poles"] = pole_match.group(1)

    # Extract Power / Horsepower (e.g., 5HP, 10 HP, 15KW)
    hp_match = re.search(r'(\d+(?:\.\d+)?)\s*(HP|KW)\b', desc, re.IGNORECASE)
    if hp_match:
        features["Power_Rating"] = hp_match.group(1)
        features["Power_UOM"] = hp_match.group(2).upper()

    # Extract Pressure (e.g., 150 PSI, 10 BAR)
    psi_match = re.search(r'(\d+(?:\.\d+)?)\s*(PSI|BAR)\b', desc, re.IGNORECASE)
    if psi_match:
        features["Pressure_Rating"] = psi_match.group(1)
        features["Pressure_UOM"] = psi_match.group(2).upper()

    # Extract NEMA / IP rating
    nema_match = re.search(r'NEMA\s*([0-9A-Za-z]+)', desc, re.IGNORECASE)
    if nema_match:
        features["NEMA_Rating"] = f"Type {nema_match.group(1).upper()}"
        
    ip_match = re.search(r'\bIP([0-9]{2})\b', desc, re.IGNORECASE)
    if ip_match:
        features["IP_Rating"] = f"IP{ip_match.group(1)}"

    # Extract Mounting Type hints
    if re.search(r'\bDIN\s*RAIL\b', desc, re.IGNORECASE):
        features["Mounting_Type"] = "DIN Rail"
    elif re.search(r'\bPANEL\s*MOUNT\b', desc, re.IGNORECASE):
        features["Mounting_Type"] = "Panel Mount"
    elif re.search(r'\bFLANGE\b', desc, re.IGNORECASE):
        features["Mounting_Type"] = "Flange Mount"
    elif re.search(r'\bTHREADED\b', desc, re.IGNORECASE):
        features["Mounting_Type"] = "Threaded"

    return features
