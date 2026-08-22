"""
Structured Specification Extraction Engine
"""

import re
from typing import Dict, Any, List, Optional
from .normalizer import normalize_uom

def extract_specifications(desc: str, part_num: str) -> Dict[str, Any]:
    """Extracts electrical, dimensional, and operational specifications from descriptor."""
    specs: Dict[str, Any] = {}
    d = desc or ""

    # Current Rating
    m_curr = re.search(r'(\d+(?:\.\d+)?)\s*(?:A|AMP|AMPS)\b', d, re.I)
    if m_curr:
        specs["Current_Rating"] = m_curr.group(1)
        specs["Current_UOM"] = "A"

    # Voltage Rating
    m_volt = re.search(r'(\d+(?:\.\d+)?)\s*(V|VAC|VDC|KV)\b', d, re.I)
    if m_volt:
        specs["Voltage_Rating"] = m_volt.group(1)
        specs["Voltage_UOM"] = m_volt.group(2).upper()

    # Poles
    m_pole = re.search(r'(\d+)\s*(?:P|POLE|POLES)\b', d, re.I)
    if m_pole:
        specs["Poles"] = m_pole.group(1)

    # Power
    m_hp = re.search(r'(\d+(?:\.\d+)?)\s*(HP|KW)\b', d, re.I)
    if m_hp:
        specs["Power_Rating"] = m_hp.group(1)
        specs["Power_UOM"] = m_hp.group(2).upper()

    # Pressure
    m_psi = re.search(r'(\d+(?:\.\d+)?)\s*(PSI|BAR)\b', d, re.I)
    if m_psi:
        specs["Pressure_Rating"] = m_psi.group(1)
        specs["Pressure_UOM"] = m_psi.group(2).upper()

    # Mounting
    if re.search(r'DIN\s*RAIL', d, re.I):
        specs["Mounting_Type"] = "DIN Rail"
    elif re.search(r'PANEL\s*MOUNT', d, re.I):
        specs["Mounting_Type"] = "Panel Mount"

    return specs
