"""
Schema Definitions and Standardization for AI-Powered Product Intelligence
Strict 252-Column Contract and Normalization Dictionaries
"""

from typing import List, Dict, Any

# Original 6 input columns
INPUT_COLUMNS = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf"
]

# Core enrichment headers
CORE_ENRICHMENT_COLUMNS = [
    # Identity & Hierarchy (24)
    "Resolved_Brand",
    "Canonical_Part_Number",
    "Normalized_Part_Number",
    "Product_Title",
    "Short_Description",
    "Long_Description",
    "Meta_Description",
    "Primary_Category",
    "Secondary_Category",
    "Tertiary_Category",
    "Category_Path",
    "UNSPSC_Code",
    "UNSPSC_Title",
    "Product_Type",
    "Series",
    "Model_Number",
    "UPC",
    "GTIN",
    "EAN",
    "MPN",
    "SKU",
    "Country_of_Origin",
    "Harmonized_Tariff_Code_HTS",
    "Lifecycle_Status",

    # Feature Bullets (10)
    "Feature_Bullet_1",
    "Feature_Bullet_2",
    "Feature_Bullet_3",
    "Feature_Bullet_4",
    "Feature_Bullet_5",
    "Feature_Bullet_6",
    "Feature_Bullet_7",
    "Feature_Bullet_8",
    "Feature_Bullet_9",
    "Feature_Bullet_10",

    # Physical Dimensions & Logistics (15)
    "Weight",
    "Weight_UOM",
    "Length",
    "Width",
    "Height",
    "Dimension_UOM",
    "Volume",
    "Volume_UOM",
    "Package_Quantity",
    "Package_Type",
    "Minimum_Order_Quantity",
    "Lead_Time_Days",
    "Hazardous_Material",
    "Prop_65_Warning",
    "Prop_65_Chemical",

    # Technical Specs & Compliance (15)
    "Warranty_Years",
    "Warranty_Description",
    "Certifications_RoHS_CE_UL",
    "NEMA_Rating",
    "IP_Rating",
    "Voltage_Rating",
    "Current_Rating",
    "Power_Rating",
    "Operating_Temperature_Min",
    "Operating_Temperature_Max",
    "Temperature_UOM",
    "Material",
    "Finish_Color",
    "Mounting_Type",
    "Connection_Type",

    # Digital Assets & Evidence (15)
    "Primary_Image_URL",
    "Image_URL_2",
    "Image_URL_3",
    "Thumbnail_URL",
    "Manufacturer_Product_URL",
    "Spec_Sheet_URL",
    "User_Manual_URL",
    "CAD_Drawing_URL",
    "SDS_MSDS_URL",
    "Installation_Guide_URL",
    "Brochure_URL",
    "Video_URL",
    "Distributor_URL_1",
    "Distributor_URL_2",
    "Reference_Source_URL",

    # Search & Cross-Reference (10)
    "Search_Keywords",
    "SEO_Title",
    "SEO_Keywords",
    "Compatible_Models",
    "Replaces_Part_Number",
    "Alternate_Part_Number",
    "Cross_Reference_Part",
    "Accessories_Included",
    "Recommended_Accessories",
    "Application_Summary",

    # Quality, Provenance & Audit (7)
    "Overall_Confidence_Score",
    "Validation_Status",
    "Review_Status",
    "Evidence_Sources_Count",
    "Provenance_Log",
    "Enrichment_Method",
    "Last_Enriched_Timestamp"
]

# Generate 50 Attribute Triplets (150 columns)
ATTRIBUTE_TRIPLET_COLUMNS: List[str] = []
for i in range(1, 51):
    ATTRIBUTE_TRIPLET_COLUMNS.extend([
        f"Attribute_Name_{i}",
        f"Attribute_Value_{i}",
        f"Attribute_UOM_{i}"
    ])

# Full 252 Expected Output Header Contract
EXPECTED_OUTPUT_COLUMNS: List[str] = (
    INPUT_COLUMNS + 
    CORE_ENRICHMENT_COLUMNS + 
    ATTRIBUTE_TRIPLET_COLUMNS
)

NUM_OUTPUT_COLUMNS = len(EXPECTED_OUTPUT_COLUMNS) # Exactly 252

# Standard Units of Measure (UOM) Normalization Dictionary (ANSI / NIST Standard)
UOM_NORMALIZATION_MAP: Dict[str, str] = {
    # Length & Dimensions
    "inch": "IN",
    "inches": "IN",
    "in": "IN",
    "\"": "IN",
    "ft": "FT",
    "foot": "FT",
    "feet": "FT",
    "'": "FT",
    "mm": "MM",
    "millimeter": "MM",
    "millimeters": "MM",
    "cm": "CM",
    "centimeter": "CM",
    "m": "M",
    "meter": "M",
    "meters": "M",

    # Weight / Mass
    "lb": "LBS",
    "lbs": "LBS",
    "pound": "LBS",
    "pounds": "LBS",
    "oz": "OZ",
    "ounce": "OZ",
    "ounces": "OZ",
    "kg": "KG",
    "kilogram": "KG",
    "kilograms": "KG",
    "g": "G",
    "gram": "G",
    "grams": "G",

    # Voltage / Electrical
    "v": "V",
    "volt": "V",
    "volts": "V",
    "vac": "VAC",
    "vdc": "VDC",
    "kv": "KV",
    "mv": "MV",
    "a": "A",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "amperes": "A",
    "ma": "MA",
    "milliamp": "MA",
    "w": "W",
    "watt": "W",
    "watts": "W",
    "kw": "KW",
    "kilowatt": "KW",
    "hp": "HP",
    "horsepower": "HP",
    "hz": "HZ",
    "hertz": "HZ",
    "khz": "KHZ",
    "mhz": "MHZ",
    "ghz": "GHZ",
    "ohm": "OHM",
    "ohms": "OHM",
    "kohm": "KOHM",
    "mohm": "MOHM",

    # Pressure
    "psi": "PSI",
    "bar": "BAR",
    "kpa": "KPA",
    "mpa": "MPA",

    # Temperature
    "deg c": "°C",
    "deg f": "°F",
    "c": "°C",
    "f": "°F",
    "celsius": "°C",
    "fahrenheit": "°F",

    # Speed & Flow
    "rpm": "RPM",
    "gpm": "GPM",
    "cfm": "CFM",
    "lpm": "LPM",

    # Volume
    "gal": "GAL",
    "gallon": "GAL",
    "gallons": "GAL",
    "l": "L",
    "liter": "L",
    "liters": "L",
    "ml": "ML"
}

# Known UNSPSC Segment / Family Mappings for Industrial Commerce
UNSPSC_TAXONOMY_MAP = {
    "circuit breaker": {"code": "39121601", "title": "Circuit breakers"},
    "contactor": {"code": "39121529", "title": "Motor contactors"},
    "relay": {"code": "39122331", "title": "Electromechanical relays"},
    "sensor": {"code": "41111900", "title": "Discrete optical sensors"},
    "proximity sensor": {"code": "41111926", "title": "Proximity sensors"},
    "photoelectric": {"code": "41111928", "title": "Photoelectric sensors"},
    "plc": {"code": "32151705", "title": "Programmable logic controllers PLC"},
    "drive": {"code": "39122001", "title": "Variable frequency drives VFD"},
    "vfd": {"code": "39122001", "title": "Variable frequency drives VFD"},
    "motor": {"code": "26101100", "title": "Electric motors"},
    "valve": {"code": "40141600", "title": "Valves"},
    "solenoid valve": {"code": "40141619", "title": "Solenoid valves"},
    "pushbutton": {"code": "39122216", "title": "Pushbutton switches"},
    "switch": {"code": "39122200", "title": "Switches"},
    "terminal block": {"code": "39121410", "title": "Terminal blocks"},
    "fuse": {"code": "39121617", "title": "Fuses"},
    "power supply": {"code": "39121004", "title": "Power supplies"},
    "encoder": {"code": "41112108", "title": "Rotary encoders"},
    "transformer": {"code": "39121002", "title": "Power transformers"},
    "bearing": {"code": "31171504", "title": "Ball bearings"},
    "pneumatic cylinder": {"code": "40141602", "title": "Pneumatic cylinders"},
    "hydraulic pump": {"code": "40151523", "title": "Hydraulic pumps"}
}

def normalize_uom(raw_uom: str) -> str:
    """Normalizes raw UOM strings into standardized abbreviations."""
    if not raw_uom:
        return ""
    cleaned = raw_uom.strip().lower().rstrip(".").replace("degrees", "deg")
    return UOM_NORMALIZATION_MAP.get(cleaned, raw_uom.strip().upper())
