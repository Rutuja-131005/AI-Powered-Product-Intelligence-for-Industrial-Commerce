"""
Exact 252-Column Contract Schema Definition
Strictly defines the 252 static commerce headers in the exact contractual sequence.
"""

from typing import List, Dict, Any

# Group 1: Source URLs (1-6)
GROUP_1_SOURCE_URLS = [
    "MFR URL",
    "Ref URL 1",
    "Ref URL 2",
    "Ref URL 3",
    "Ref URL 4",
    "Ref URL 5"
]

# Group 2: Taxonomy & Core Identifiers (7-23)
GROUP_2_CORE_IDENTIFIERS = [
    "PART_NUMBER",
    "Dept",
    "Class",
    "Fine",
    "SKU - MY_PART_NUMBER",
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf",
    "MANUFACTURER_NAME",
    "BRAND_NAME",
    "TRADE_NAME",
    "MANUFACTURER_PART_NUMBER",
    "ALTERNATE_PART_NUMBER",
    "Classpath"
]

# Group 3: Commerce Descriptions (24-29)
GROUP_3_DESCRIPTIONS = [
    "MOBILE_DESC",
    "INVOICE_DESC",
    "SHORT_DESC",
    "LONG_DESC1",
    "RETAIL_DESC",
    "MARKETING_DESCRIPTION"
]

# Group 4: 20 Item Feature Bullets (30-49)
GROUP_4_FEATURES = [f"ITEM_FEATURES_{i}" for i in range(1, 21)]

# Group 5: Additional Commerce Metadata (50-55)
GROUP_5_METADATA = [
    "With",
    "Standard/Approvals",
    "Prop 65",
    "Application",
    "Includes",
    "Product Name"
]

# Group 6: 50 Attribute Triplets (56-205) -> (ATTRIBUTE_LABEL i, ATTRIBUTE_VALUE i, ATTRIBUTE_UOM i)
GROUP_6_ATTRIBUTES = []
for i in range(1, 51):
    GROUP_6_ATTRIBUTES.extend([
        f"ATTRIBUTE_LABEL {i}",
        f"ATTRIBUTE_VALUE {i}",
        f"ATTRIBUTE_UOM {i}"
    ])

# Group 7: Commercial & Dimensions (206-224)
GROUP_7_COMMERCIAL_DIMENSIONS = [
    "UPC",
    "EAN",
    "GTIN",
    "UNSPSC",
    "Warranty",
    "List Price",
    "Selling Qty",
    "Selling UOM",
    "Standard Packaging Information",
    "LENGTH",
    "LENGTH_UOM",
    "HEIGHT",
    "HEIGHT_UOM",
    "WIDTH",
    "WIDTH_UOM",
    "WEIGHT",
    "WEIGHT_UOM",
    "VOLUME",
    "VOLUME_UOM"
]

# Group 8: Digital Assets & Technical Documents (225-249)
GROUP_8_ASSETS_DOCUMENTS = [
    "Product Image",
    "Alternate Image 1",
    "Alternate Image 2",
    "Alternate Image 3",
    "Alternate Image 4",
    "SDS",
    "SDS_1",
    "Warranty Information",
    "Catalog",
    "Specification Sheet",
    "Instruction/Installation Manual",
    "Service Manual",
    "Owners/User Manual",
    "Line Drawing",
    "MTR",
    "RoHS",
    "Full Engineering Drawing",
    "Energy Star Guide",
    "Technical Bulletin",
    "Submittal",
    "Compatibility Chart",
    "Size Chart",
    "Product Label/Insert",
    "Video Link",
    "Video Link 1"
]

# Group 9: Operational Flags (250-252)
GROUP_9_FLAGS = [
    "Country Of Origin",
    "Discontinued",
    "Actual Image (Yes/No)"
]

# Combined Final Contractual 252 Headers in Exact Order
FINAL_252_HEADERS: List[str] = (
    GROUP_1_SOURCE_URLS +
    GROUP_2_CORE_IDENTIFIERS +
    GROUP_3_DESCRIPTIONS +
    GROUP_4_FEATURES +
    GROUP_5_METADATA +
    GROUP_6_ATTRIBUTES +
    GROUP_7_COMMERCIAL_DIMENSIONS +
    GROUP_8_ASSETS_DOCUMENTS +
    GROUP_9_FLAGS
)

# Raw 6 input fields that must be 100% preserved
ORIGINAL_INPUT_HEADERS = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf"
]

GROUP_1_SOURCE_INPUT = ORIGINAL_INPUT_HEADERS

assert len(FINAL_252_HEADERS) == 252, f"Header count mismatch: expected 252, got {len(FINAL_252_HEADERS)}"
