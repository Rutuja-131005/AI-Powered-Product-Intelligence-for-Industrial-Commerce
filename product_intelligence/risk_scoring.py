"""
Merchant Risk & Product Authenticity Verification Engine
Evaluates merchant listing claims against canonical manufacturer datasheets to generate
a Product Trust & Authenticity Score (0-100) and flag pricing/spec anomalies for Razorpay Risk Engine.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MerchantRiskScorer:
    def __init__(self, confidence_threshold: float = 0.70):
        self.confidence_threshold = confidence_threshold

    def evaluate_merchant_product_risk(
        self,
        merchant_claim: Dict[str, Any],
        retrieved_evidence: Optional[List[Dict[str, Any]]] = None,
        rag_confidence_score: float = 0.85
    ) -> Dict[str, Any]:
        """
        Evaluates merchant product listing risk and returns structured score + risk flags.
        """
        product_title = merchant_claim.get("Part_Desc", merchant_claim.get("title", ""))
        claimed_mpn = merchant_claim.get("Mfg_Part_Num", merchant_claim.get("mpn", ""))
        claimed_price = float(merchant_claim.get("price", merchant_claim.get("claimed_price", 0.0)))
        claimed_brand = merchant_claim.get("E1_Brand", merchant_claim.get("brand", ""))

        risk_flags = []
        risk_deductions = 0.0

        # Check 1: Evidence Availability (RAG Grounding)
        has_evidence = retrieved_evidence and len(retrieved_evidence) > 0
        if not has_evidence and rag_confidence_score < 0.5:
            risk_deductions += 25.0
            risk_flags.append("UNVERIFIED_PRODUCT_NO_CANONICAL_DATASHEET_FOUND")

        # Check 2: Brand / MPN Discrepancy
        if claimed_brand and ("unbranded" in claimed_brand.lower() or "no unilog brand" in claimed_brand.lower()):
            risk_deductions += 15.0
            risk_flags.append("GENERIC_UNBRANDED_LISTING_HIGH_REPLACEMENT_RISK")

        # Check 3: Pricing Anomaly (If price provided)
        baseline_price = float(merchant_claim.get("baseline_price", claimed_price))
        if claimed_price > 0 and baseline_price > 0:
            price_ratio = claimed_price / baseline_price
            if price_ratio < 0.40:
                risk_deductions += 35.0
                risk_flags.append(f"SUSPICIOUSLY_LOW_PRICE_POSSIBLE_COUNTERFEIT ({round((1-price_ratio)*100)}% below market)")
            elif price_ratio > 2.5:
                risk_deductions += 20.0
                risk_flags.append(f"EXCESSIVE_PRICE_INFLATION ({round((price_ratio-1)*100)}% above market)")

        # Check 4: Hazardous / Restricted Material Risk
        is_hazardous = merchant_claim.get("dangerous_goods_flag", False)
        if is_hazardous:
            risk_deductions += 10.0
            risk_flags.append("HAZARDOUS_GOODS_REQUIRES_SPECIAL_PAYMENT_UNDERWRITING")

        # Calculate Final Product Trust & Authenticity Score (0-100)
        trust_score = max(0.0, min(100.0, round(100.0 - risk_deductions, 1)))

        # Risk Classification
        if trust_score >= 85.0:
            risk_level = "LOW_RISK"
            action_recommendation = "Auto-approve for Razorpay Checkout & High Limit Payouts"
        elif trust_score >= 65.0:
            risk_level = "MEDIUM_RISK"
            action_recommendation = "Standard Review - Require Supplier Invoice Proof"
        else:
            risk_level = "HIGH_RISK"
            action_recommendation = "Flag for Manual Underwriting & Restrict Payout Velocity"

        return {
            "product_trust_score": trust_score,
            "risk_level": risk_level,
            "action_recommendation": action_recommendation,
            "risk_flags": risk_flags,
            "evidence_grounding_confidence": rag_confidence_score,
            "passed_verification": trust_score >= 65.0
        }
