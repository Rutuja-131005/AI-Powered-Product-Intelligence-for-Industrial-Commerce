"""
252-Column Fixed Output Schema Definitions based on TRD Header Groups
"""

from typing import List

# Group 1: Source / Identity Input Fields (1–6)
GROUP_1_SOURCE_INPUT = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf"
]

# Group 2: Core Identifiers & Taxonomy (7–23: 17 columns)
GROUP_2_CORE_IDENTIFIERS = [
    "PRODUCT_NAME",
    "MANUFACTURER",
    "BRAND_NAME",
    "CANONICAL_PART_NUMBER",
    "NORMALIZED_PART_NUMBER",
    "PRIMARY_CATEGORY",
    "SECONDARY_CATEGORY",
    "TERTIARY_CATEGORY",
    "CATEGORY_PATH",
    "UNSPSC_CODE",
    "UNSPSC_TITLE",
    "PRODUCT_TYPE",
    "SERIES_NAME",
    "MODEL_NUMBER",
    "UPC",
    "GTIN",
    "EAN"
]

# Group 3: Descriptions (24–29: 6 columns)
GROUP_3_DESCRIPTIONS = [
    "MOBILE_DESC",
    "INVOICE_DESC",
    "SHORT_DESC",
    "LONG_DESC1",
    "RETAIL_DESC",
    "MARKETING_DESCRIPTION"
]

# Group 4: Feature Bullets (30–49: 20 columns)
GROUP_4_FEATURES = [f"ITEM_FEATURES_{i}" for i in range(1, 21)]

# Group 5: With / Approvals / Application / Includes / Search (50–55: 6 columns)
GROUP_5_COMMERCE_METADATA = [
    "WITH",
    "APPROVALS_STANDARDS",
    "APPLICATION",
    "INCLUDES",
    "SEARCH_KEYWORDS",
    "SEO_TITLE"
]

# Group 6: Attribute Slots 1–50 (56–205: 150 columns)
GROUP_6_ATTRIBUTES: List[str] = []
for i in range(1, 51):
    GROUP_6_ATTRIBUTES.extend([
        f"ATTR_NAME_{i}",
        f"ATTR_VALUE_{i}",
        f"ATTR_UOM_{i}"
    ])

# Group 7: Identifiers / Commercial / Packaging / Dimensions (206–224: 19 columns)
GROUP_7_PHYSICAL_LOGISTICS = [
    "WEIGHT",
    "WEIGHT_UOM",
    "LENGTH",
    "WIDTH",
    "HEIGHT",
    "DIMENSION_UOM",
    "VOLUME",
    "VOLUME_UOM",
    "PACKAGE_QTY",
    "PACKAGE_TYPE",
    "MIN_ORDER_QTY",
    "LEAD_TIME_DAYS",
    "HAZARDOUS_MATERIAL",
    "PROP_65_WARNING",
    "PROP_65_CHEMICAL",
    "WARRANTY_YEARS",
    "WARRANTY_DESC",
    "NEMA_RATING",
    "IP_RATING"
]

# Group 8: Images / Assets / Documents / Ratings (225–249: 25 columns)
GROUP_8_ASSETS_RATINGS = [
    "PRIMARY_IMAGE_URL",
    "IMAGE_URL_2",
    "IMAGE_URL_3",
    "THUMBNAIL_URL",
    "MANUFACTURER_URL",
    "SPEC_SHEET_URL",
    "USER_MANUAL_URL",
    "CAD_DRAWING_URL",
    "SDS_MSDS_URL",
    "INSTALLATION_GUIDE_URL",
    "BROCHURE_URL",
    "VIDEO_URL",
    "DISTRIBUTOR_URL_1",
    "DISTRIBUTOR_URL_2",
    "REFERENCE_SOURCE_URL",
    "REPLACES_PART_NUMBER",
    "ALT_PART_NUMBER",
    "CROSS_REFERENCE_PART",
    "VOLTAGE_RATING",
    "CURRENT_RATING",
    "POWER_RATING",
    "TEMP_MIN",
    "TEMP_MAX",
    "MATERIAL",
    "MOUNTING_TYPE"
]

# Group 9: Country / Discontinued / Image Flag (250–252: 3 columns)
GROUP_9_FLAGS = [
    "COUNTRY_OF_ORIGIN",
    "DISCONTINUED_STATUS",
    "IMAGE_FLAG"
]

# Exact 252 Output Column Contract
FINAL_252_HEADERS: List[str] = (
    GROUP_1_SOURCE_INPUT +
    GROUP_2_CORE_IDENTIFIERS +
    GROUP_3_DESCRIPTIONS +
    GROUP_4_FEATURES +
    GROUP_5_COMMERCE_METADATA +
    GROUP_6_ATTRIBUTES +
    GROUP_7_PHYSICAL_LOGISTICS +
    GROUP_8_ASSETS_RATINGS +
    GROUP_9_FLAGS
)

assert len(FINAL_252_HEADERS) == 252, f"Expected 252 headers, got {len(FINAL_252_HEADERS)}"
