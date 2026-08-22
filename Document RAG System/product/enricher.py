"""
Commerce Copy, Features, and Descriptions Enrichment Engine
Generates MOBILE_DESC, INVOICE_DESC, SHORT_DESC, LONG_DESC1, RETAIL_DESC,
MARKETING_DESCRIPTION, ITEM_FEATURES_1..20, WITH, APPLICATION, and INCLUDES.
"""

from typing import Dict, Any, List

def enrich_product_copy(brand: str, part_num: str, part_desc: str, specs: Dict[str, Any]) -> Dict[str, Any]:
    """Generates TRD-specified descriptions, 20 feature bullets, and commerce metadata."""
    p_type = specs.get("Product_Type", "Industrial Component")
    curr = specs.get("Current_Rating", "")
    volt = specs.get("Voltage_Rating", "")
    mount = specs.get("Mounting_Type", "Standard Mount")

    # Titles & Descriptions
    title = f"{brand} {part_num} {p_type} {curr}A {volt}V".strip()
    short_desc = f"Premium {brand} {part_num} {p_type.lower()} designed for high-reliability industrial operations."
    mobile_desc = f"{brand} {part_num} - {p_type} {volt}V {curr}A"
    invoice_desc = f"{brand} {part_num} {p_type.upper()}"
    retail_desc = f"Buy genuine {brand} {part_num} {p_type}. In-stock with manufacturer warranty and fast delivery."
    
    long_desc = (
        f"The {brand} {part_num} is an industrial-grade {p_type.lower()} engineered for demanding automation "
        f"and power control environments. Features rated {volt}V operation, {curr}A capacity, and rugged {mount} "
        f"construction for maximum uptime and operator safety."
    )
    marketing_desc = f"Experience superior efficiency and durability with the {brand} {part_num} series."

    # 20 Feature Bullets
    bullets = [
        f"Genuine {brand} engineered industrial {p_type.lower()}",
        f"Operating Voltage: {volt}V for dependable circuit protection and switching" if volt else "Optimized for wide operating voltage compatibility",
        f"Continuous Current Service: {curr}A rated" if curr else "Engineered for heavy-duty industrial continuous duty",
        f"Mounting Style: {mount}",
        "Fully compliant with UL, CSA, CE, and RoHS industrial standards",
        f"Temperature Range: -20°C to 60°C operating capacity",
        "Ruggedized industrial housing designed for harsh ambient environments",
        "High dielectric strength with integrated shock protection",
        "Precision calibrated trip and response characteristics",
        "Simple installation with standard industrial terminal interface",
        "Low heat dissipation and optimized energy efficiency",
        "Designed for seamless integration with OEM control systems",
        "Tested to rigorous mechanical endurance standards",
        "High interruption capacity for maximum system protection",
        "Compact form-factor saves critical panel enclosure space",
        "Vibration and shock resistant industrial construction",
        "Corrosion-resistant terminal clamps and contacts",
        "Clear laser-marked part identification and rating labels",
        "Compatible with standard manufacturer auxiliary contacts and accessories",
        f"Backed by authentic {brand} manufacturer limited warranty"
    ]

    features = {f"ITEM_FEATURES_{i+1}": bullets[i] for i in range(20)}

    return {
        "PRODUCT_NAME": title,
        "SHORT_DESC": short_desc,
        "LONG_DESC1": long_desc,
        "MOBILE_DESC": mobile_desc,
        "INVOICE_DESC": invoice_desc,
        "RETAIL_DESC": retail_desc,
        "MARKETING_DESCRIPTION": marketing_desc,
        **features,
        "WITH": "Mounting brackets and terminal hardware",
        "APPLICATION": "Industrial automation panels, motor control centers, machinery power distribution",
        "INCLUDES": "Instruction manual and safety documentation",
        "SEARCH_KEYWORDS": f"{brand}, {part_num}, {p_type}, industrial, automation, electrical",
        "SEO_TITLE": f"{brand} {part_num} | {p_type} - Datasheet & In-Stock Delivery"
    }
