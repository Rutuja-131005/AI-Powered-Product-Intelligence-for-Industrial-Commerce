"""
Source Ranker Module
Ranks external source links by authority (Manufacturer > Distributor > General Spec).
"""

from typing import Dict, Any, List

def rank_sources(sources_dict: Dict[str, str]) -> List[Dict[str, Any]]:
    """Ranks discovered source URLs based on domain authority."""
    ranked = []
    for key, url in sources_dict.items():
        if not url:
            continue
        priority = 10
        if "MFR" in key or "official" in url.lower():
            priority = 1
        elif "Spec" in key or "datasheet" in url.lower():
            priority = 2
        elif "Manual" in key or "manual" in url.lower():
            priority = 3
        elif "CAD" in key or "3D" in url.lower():
            priority = 4
        elif "SDS" in key or "msds" in url.lower():
            priority = 5
        elif "Ref" in key:
            priority = 6

        ranked.append({
            "key": key,
            "url": url,
            "priority": priority
        })

    ranked.sort(key=lambda x: x["priority"])
    return ranked
