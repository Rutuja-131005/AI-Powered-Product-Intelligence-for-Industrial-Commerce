"""
Sources Search Module
Discovers authoritative manufacturer portals, distributors, datasheets, and manuals.
"""

from typing import Dict, Any, List
from sources.discovery import discover_product_sources

def search_sources(brand: str, part_number: str) -> Dict[str, str]:
    """Discovers external source links for a given brand and part number."""
    return discover_product_sources(brand, part_number)
