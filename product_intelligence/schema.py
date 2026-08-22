"""
Strict 252-Column Schema Definition & Constants
Matches the contractual output headers in exact order.
"""

from typing import Optional, Dict
from export.output_schema import (
    FINAL_252_HEADERS,
    ORIGINAL_INPUT_HEADERS,
    GROUP_1_SOURCE_URLS,
    GROUP_2_CORE_IDENTIFIERS,
    GROUP_3_DESCRIPTIONS,
    GROUP_4_FEATURES,
    GROUP_5_METADATA,
    GROUP_6_ATTRIBUTES,
    GROUP_7_COMMERCIAL_DIMENSIONS,
    GROUP_8_ASSETS_DOCUMENTS,
    GROUP_9_FLAGS
)

EXPECTED_OUTPUT_COLUMNS = FINAL_252_HEADERS
INPUT_COLUMNS = ORIGINAL_INPUT_HEADERS
NUM_OUTPUT_COLUMNS = 252

ATTRIBUTE_TRIPLET_COLUMNS = GROUP_6_ATTRIBUTES

STANDARD_UOM_MAP = {
    "v": "V", "vac": "VAC", "vdc": "VDC", "volt": "V", "volts": "V",
    "a": "A", "amp": "A", "amps": "A", "ampere": "A", "amperes": "A",
    "hp": "HP", "horsepower": "HP", "kw": "KW", "w": "W", "watt": "W", "watts": "W",
    "hz": "Hz", "hertz": "Hz", "psi": "PSI", "bar": "bar", "kpa": "kPa",
    "in": "IN", "inch": "IN", "inches": "IN", '"': "IN",
    "ft": "FT", "feet": "FT", "foot": "FT",
    "mm": "MM", "cm": "CM", "m": "M",
    "lbs": "LBS", "lb": "LBS", "pound": "LBS", "pounds": "LBS",
    "kg": "KG", "g": "G", "oz": "OZ",
    "deg c": "°C", "c": "°C", "deg f": "°F", "f": "°F"
}

def normalize_uom(uom_str: Optional[str]) -> str:
    """Standardizes unit strings into ANSI/NIST representations."""
    if not uom_str:
        return ""
    cleaned = str(uom_str).strip().lower()
    return STANDARD_UOM_MAP.get(cleaned, str(uom_str).strip().upper())

UNSPSC_TAXONOMY_MAP: Dict[str, str] = {
    "CIRCUIT BREAKER": "39121601",
    "CONTACTOR": "39121529",
    "MOTOR STARTER": "39121521",
    "PLC": "32151705",
    "VARIABLE FREQUENCY DRIVE": "39122001",
    "PRESSURE TRANSMITTER": "41112410",
    "FLOW METER": "41112501",
    "TEMPERATURE SENSOR": "41112212",
    "PROXIMITY SENSOR": "39122230",
    "ENCLOSURE": "39121324",
    "RELAY": "39122300"
}
