"""
Attribute & Unit Normalization Engine
"""

import re
from typing import Dict, Any, Optional

UOM_MAP = {
    "inch": "IN", "inches": "IN", "in": "IN", "\"": "IN",
    "ft": "FT", "foot": "FT", "feet": "FT", "'": "FT",
    "mm": "MM", "millimeter": "MM", "cm": "CM", "m": "M",
    "lb": "LBS", "lbs": "LBS", "pound": "LBS", "pounds": "LBS",
    "oz": "OZ", "kg": "KG", "g": "G",
    "v": "V", "volt": "V", "volts": "V", "vac": "VAC", "vdc": "VDC", "kv": "KV",
    "a": "A", "amp": "A", "amps": "A", "ma": "MA",
    "w": "W", "watt": "W", "kw": "KW", "hp": "HP",
    "hz": "HZ", "khz": "KHZ", "mhz": "MHZ",
    "psi": "PSI", "bar": "BAR",
    "deg c": "°C", "deg f": "°F", "c": "°C", "f": "°F",
    "rpm": "RPM", "gpm": "GPM", "cfm": "CFM"
}

def normalize_uom(raw_uom: Optional[str]) -> str:
    if not raw_uom:
        return ""
    cleaned = raw_uom.strip().lower().rstrip(".").replace("degrees", "deg")
    return UOM_MAP.get(cleaned, raw_uom.strip().upper())

def normalize_category_path(path: str) -> str:
    if not path:
        return ""
    return re.sub(r'\s*[/>|]\s*', ' > ', path.strip())
