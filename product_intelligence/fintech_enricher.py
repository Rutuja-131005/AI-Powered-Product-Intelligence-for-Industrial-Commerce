"""
Fintech & Compliance Data Enrichment Module
Enriches product catalogs with HSN/SAC codes, GST tax slabs, commercial shipping dimensions,
and return/warranty policy metadata required for Razorpay Magic Checkout & e-commerce.
"""

import os
import csv
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Fallback HSN/GST Lookup Table
DEFAULT_HSN_LOOKUP = {
    "abrasive": ("8467", 18.0),
    "belt": ("8467", 18.0),
    "disc": ("8467", 18.0),
    "motor": ("8501", 18.0),
    "breaker": ("8536", 18.0),
    "switch": ("8536", 18.0),
    "plc": ("8537", 18.0),
    "controller": ("8537", 18.0),
    "drive": ("8504", 18.0),
    "vfd": ("8504", 18.0),
    "inverter": ("8504", 18.0),
    "transmitter": ("9026", 18.0),
    "sensor": ("9031", 18.0),
    "enclosure": ("3926", 18.0),
    "relay": ("8511", 18.0),
    "lubricant": ("3403", 18.0),
    "gas": ("2804", 28.0),
    "valve": ("8481", 18.0),
    "bearing": ("8483", 18.0),
    "screw": ("7318", 18.0),
    "bolt": ("7318", 18.0)
}

class FintechEnricher:
    def __init__(self, master_csv_path: Optional[str] = None):
        self.master_path = master_csv_path or os.path.join("data", "hsn_gst_master.csv")
        self.hsn_map = self._load_hsn_master()

    def _load_hsn_master(self) -> Dict[str, Dict[str, Any]]:
        """Loads HSN master reference table if present."""
        hsn_map = {}
        if os.path.exists(self.master_path):
            try:
                with open(self.master_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        hsn_code = row.get("HSN_Code", "").strip()
                        if hsn_code:
                            hsn_map[hsn_code] = {
                                "category": row.get("Category_Description", ""),
                                "gst_rate": float(row.get("Default_GST_Rate", 18.0)),
                                "dangerous": row.get("Dangerous_Goods", "False").lower() == "true",
                                "volumetric_risk": row.get("Volumetric_Risk", "Low")
                            }
            except Exception as e:
                logger.error(f"Error loading HSN master CSV: {e}")
        return hsn_map

    def predict_hsn_and_gst(self, title: str, category: str = "", part_number: str = "") -> Dict[str, Any]:
        """
        Predicts 6/8-digit HSN code and GST tax slab based on product text.
        """
        text = f"{title} {category} {part_number}".lower()

        # Check default keyword lookup
        predicted_hsn = "8467"  # Default industrial machinery/tools
        predicted_gst = 18.0
        dangerous_flag = False
        volumetric_risk = "Low"

        for kw, (hsn, gst) in DEFAULT_HSN_LOOKUP.items():
            if kw in text:
                predicted_hsn = hsn
                predicted_gst = gst
                break

        # Override from master map if matched
        if predicted_hsn in self.hsn_map:
            master_data = self.hsn_map[predicted_hsn]
            predicted_gst = master_data.get("gst_rate", predicted_gst)
            dangerous_flag = master_data.get("dangerous", dangerous_flag)
            volumetric_risk = master_data.get("volumetric_risk", volumetric_risk)

        return {
            "hsn_sac_code": predicted_hsn,
            "gst_rate_pct": predicted_gst,
            "dangerous_goods_flag": dangerous_flag,
            "volumetric_risk": volumetric_risk
        }

    def estimate_shipping_dimensions(self, title: str, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Estimates commercial package weight, dimensions, and freight class for Magic Checkout.
        """
        attrs = attributes or {}
        text = f"{title} {json_to_str(attrs)}".lower()

        # Extract numeric weight if present (e.g. 5 lbs, 2.5 kg)
        net_weight_kg = 0.5  # default baseline 0.5kg
        match_kg = re.search(r'(\d+(?:\.\d+)?)\s*(kg|kilo)', text)
        match_lbs = re.search(r'(\d+(?:\.\d+)?)\s*(lbs?|pound)', text)

        if match_kg:
            net_weight_kg = float(match_kg.group(1))
        elif match_lbs:
            net_weight_kg = round(float(match_lbs.group(1)) * 0.453592, 2)

        gross_weight_kg = round(net_weight_kg * 1.15, 2)  # +15% packaging
        volumetric_weight_kg = round(gross_weight_kg * 1.1, 2)
        freight_class = "Class 70 (Standard Parcel)" if gross_weight_kg < 30 else "Class 100 (Freight/LTL)"

        return {
            "net_weight_kg": net_weight_kg,
            "gross_weight_kg": gross_weight_kg,
            "volumetric_weight_kg": volumetric_weight_kg,
            "freight_class": freight_class,
            "shipping_ready_flag": True
        }

    def enrich_fintech_metadata(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main enrichment function combining tax, shipping, and warranty specs.
        """
        title = product_data.get("Part_Desc", product_data.get("product_title", ""))
        part_num = product_data.get("Mfg_Part_Num", product_data.get("mpn", ""))
        category = product_data.get("category", "")
        attrs = product_data.get("extracted_attributes", {})

        tax_info = self.predict_hsn_and_gst(title, category, part_num)
        shipping_info = self.estimate_shipping_dimensions(title, attrs)

        return {
            **tax_info,
            **shipping_info,
            "warranty_period": "12 Months Manufacturer Warranty",
            "return_eligibility": "14-Day Industrial Return / Replacement Only",
            "magic_checkout_ready": True
        }

def json_to_str(val: Any) -> str:
    if isinstance(val, dict):
        return " ".join([f"{k} {v}" for k, v in val.items()])
    return str(val or "")
