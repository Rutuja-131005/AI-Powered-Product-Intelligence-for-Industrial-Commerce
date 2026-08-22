"""
Source Discovery Engine
Generates search queries and matches manufacturer portals and distributor links.
"""

import urllib.parse
from typing import Dict, List, Any

# Authoritative manufacturer portal templates
MANUFACTURER_PORTALS = {
    "Allen-Bradley": {
        "domain": "rockwellautomation.com",
        "base_url": "https://www.rockwellautomation.com",
        "search_url": "https://www.rockwellautomation.com/en-us/search.html?q=",
        "spec_sheet_base": "https://literature.rockwellautomation.com/idc/groups/literature/documents/td/",
        "cad_base": "https://www.rockwellautomation.com/en-us/support/documentation/cad-drawings.html"
    },
    "Schneider Electric": {
        "domain": "se.com",
        "base_url": "https://www.se.com",
        "search_url": "https://www.se.com/us/en/search/?q=",
        "spec_sheet_base": "https://download.schneider-electric.com/files?p_Doc_Ref=",
        "cad_base": "https://www.se.com/us/en/work/products/product-cad.jsp"
    },
    "Square D": {
        "domain": "se.com",
        "base_url": "https://www.se.com/us/en/brands/squared/",
        "search_url": "https://www.se.com/us/en/search/?q=",
        "spec_sheet_base": "https://download.schneider-electric.com/files?p_Doc_Ref=",
        "cad_base": "https://www.se.com/us/en/work/products/product-cad.jsp"
    },
    "Siemens": {
        "domain": "siemens.com",
        "base_url": "https://www.siemens.com",
        "search_url": "https://mall.industry.siemens.com/mall/en/ww/Catalog/Products/?searchTerm=",
        "spec_sheet_base": "https://support.industry.siemens.com/cs/document/",
        "cad_base": "https://support.industry.siemens.com/cs/sc/3118/3d-cad"
    },
    "Eaton": {
        "domain": "eaton.com",
        "base_url": "https://www.eaton.com",
        "search_url": "https://www.eaton.com/us/en-us/search.html?q=",
        "spec_sheet_base": "https://www.eaton.com/content/dam/eaton/products/",
        "cad_base": "https://www.eaton.com/us/en-us/support/cad-drawings.html"
    },
    "ABB": {
        "domain": "abb.com",
        "base_url": "https://new.abb.com",
        "search_url": "https://new.abb.com/search/en/results?q=",
        "spec_sheet_base": "https://search.abb.com/library/Download.aspx?DocumentID=",
        "cad_base": "https://new.abb.com/low-voltage/support/3d-cad"
    },
    "Honeywell": {
        "domain": "honeywell.com",
        "base_url": "https://sps.honeywell.com",
        "search_url": "https://sps.honeywell.com/us/en/search?q=",
        "spec_sheet_base": "https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/",
        "cad_base": "https://sps.honeywell.com/us/en/resources/drawings"
    },
    "Parker Hannifin": {
        "domain": "parker.com",
        "base_url": "https://www.parker.com",
        "search_url": "https://www.parker.com/us/en/search.html?query=",
        "spec_sheet_base": "https://www.parker.com/content/dam/Parker-com/Literature/",
        "cad_base": "https://www.parker.com/us/en/support/cad-drawings.html"
    }
}

DISTRIBUTOR_PORTALS = {
    "Grainger": "https://www.grainger.com/search?searchQuery=",
    "Radwell": "https://www.radwell.com/en-US/Buy?SearchTerm=",
    "DigiKey": "https://www.digikey.com/en/products/result?keywords=",
    "Mouser": "https://www.mouser.com/c/?q="
}

def generate_discovery_queries(part_number: str, brand: str, manufacturer: str) -> List[str]:
    """Generates standard TRD search discovery query templates."""
    pn = part_number.strip()
    return [
        f'"{pn}" "{manufacturer}"',
        f'"{pn}" "{brand}"',
        f'"{pn}" specification',
        f'"{pn}" filetype:pdf',
        f'"{pn}" site:{MANUFACTURER_PORTALS.get(brand, {}).get("domain", "industrial.com")}'
    ]

def discover_product_sources(brand: str, part_number: str) -> Dict[str, str]:
    """Discovers authoritative URLs and reference endpoints for a given product."""
    encoded_pn = urllib.parse.quote_plus(part_number)
    encoded_brand_pn = urllib.parse.quote_plus(f"{brand} {part_number}")
    
    brand_cfg = MANUFACTURER_PORTALS.get(brand)
    if brand_cfg:
        manuf_url = f"{brand_cfg['search_url']}{encoded_pn}"
        spec_url = f"{brand_cfg['search_url']}{encoded_pn}+datasheet"
        manual_url = f"{brand_cfg['search_url']}{encoded_pn}+manual"
        cad_url = f"{brand_cfg['cad_base']}?q={encoded_pn}"
    else:
        manuf_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' official website')}"
        spec_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' datasheet pdf')}"
        manual_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' manual pdf')}"
        cad_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' 3D CAD model')}"

    return {
        "Manufacturer_Product_URL": manuf_url,
        "Spec_Sheet_URL": spec_url,
        "User_Manual_URL": manual_url,
        "CAD_Drawing_URL": cad_url,
        "SDS_MSDS_URL": f"https://www.msdsdigital.com/search?q={encoded_brand_pn}",
        "Installation_Guide_URL": f"{manual_url}+installation",
        "Brochure_URL": f"{spec_url}+brochure",
        "Video_URL": f"https://www.youtube.com/results?search_query={encoded_brand_pn}",
        "Distributor_URL_1": f"{DISTRIBUTOR_PORTALS['Grainger']}{encoded_pn}",
        "Distributor_URL_2": f"{DISTRIBUTOR_PORTALS['Radwell']}{encoded_pn}",
        "Reference_Source_URL": f"https://www.globalspec.com/search/all?query={encoded_brand_pn}"
    }
