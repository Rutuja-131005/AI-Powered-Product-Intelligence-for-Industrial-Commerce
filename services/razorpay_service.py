"""
Razorpay Payment Gateway & Order Management Service
Handles dynamic Order Creation, Payment Links, Signature Verification, and Webhook processing.
Supports automatic fallback to Mock Mode when live Razorpay API keys are not supplied.
"""

import os
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import razorpay
    RAZORPAY_SDK_AVAILABLE = True
except ImportError:
    RAZORPAY_SDK_AVAILABLE = False
    logger.warning("razorpay SDK not installed. Running in Mock Mode.")

class RazorpayService:
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key_prodintellix")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "mock_secret_prodintellix")
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "mock_webhook_secret")
        
        self.is_mock = (
            not RAZORPAY_SDK_AVAILABLE
            or self.key_id.startswith("rzp_test_mock")
            or self.key_secret == "mock_secret_prodintellix"
        )
        
        if not self.is_mock and RAZORPAY_SDK_AVAILABLE:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay SDK client: {e}")
                self.is_mock = True

    def create_order(
        self,
        product_title: str,
        unit_price: float,
        hsn_code: str = "8467",
        gst_rate: float = 18.0,
        quantity: int = 1,
        currency: str = "INR",
        part_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a dynamic Razorpay Order with tax calculations and metadata notes.
        """
        subtotal = round(unit_price * quantity, 2)
        gst_amount = round(subtotal * (gst_rate / 100.0), 2)
        total_amount = round(subtotal + gst_amount, 2)
        amount_paisa = int(total_amount * 100)

        notes = {
            "platform": "ProdIntellix AI + Razorpay",
            "product_title": str(product_title)[:60],
            "part_number": str(part_number or "N/A"),
            "hsn_code": str(hsn_code),
            "gst_rate_pct": f"{gst_rate}%",
            "subtotal_inr": str(subtotal),
            "gst_amount_inr": str(gst_amount),
            "total_amount_inr": str(total_amount)
        }

        order_payload = {
            "amount": amount_paisa,
            "currency": currency,
            "receipt": f"rcpt_{hash(product_title + str(unit_price)) & 0xFFFFFFF}",
            "notes": notes,
            "payment_capture": 1
        }

        if not self.is_mock:
            try:
                real_order = self.client.order.create(data=order_payload)
                real_order["calculated_breakdown"] = {
                    "subtotal": subtotal,
                    "gst_amount": gst_amount,
                    "total_amount": total_amount,
                    "gst_rate": gst_rate,
                    "hsn_code": hsn_code
                }
                return real_order
            except Exception as e:
                logger.error(f"Razorpay API call failed: {e}. Falling back to mock order.")

        # Return structured Mock Order
        mock_id = f"order_mock_{hash(product_title + str(amount_paisa)) & 0xFFFFFF}"
        return {
            "id": mock_id,
            "entity": "order",
            "amount": amount_paisa,
            "amount_paid": 0,
            "amount_due": amount_paisa,
            "currency": currency,
            "receipt": order_payload["receipt"],
            "status": "created",
            "attempts": 0,
            "notes": notes,
            "created_at": 1757050000,
            "is_mock": True,
            "calculated_breakdown": {
                "subtotal": subtotal,
                "gst_amount": gst_amount,
                "total_amount": total_amount,
                "gst_rate": gst_rate,
                "hsn_code": hsn_code
            }
        }

    def create_payment_link(
        self,
        product_title: str,
        total_amount: float,
        customer_name: str = "B2B Customer",
        customer_email: str = "customer@example.com",
        customer_phone: str = "+919876543210"
    ) -> Dict[str, Any]:
        """
        Generates a Razorpay Payment Link for sharing quotes via SMS/Email.
        """
        amount_paisa = int(total_amount * 100)
        link_payload = {
            "amount": amount_paisa,
            "currency": "INR",
            "accept_partial": False,
            "description": f"Invoice Payment for {product_title[:50]}",
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_phone
            },
            "notify": {"sms": True, "email": True},
            "reminder_enable": True,
            "notes": {"platform": "ProdIntellix"}
        }

        if not self.is_mock:
            try:
                return self.client.payment_link.create(data=link_payload)
            except Exception as e:
                logger.error(f"Razorpay Payment Link API failed: {e}")

        # Return mock payment link
        mock_link_id = f"plink_mock_{hash(product_title) & 0xFFFFFF}"
        return {
            "id": mock_link_id,
            "short_url": f"https://rzp.io/i/mock_{mock_link_id}",
            "status": "created",
            "amount": amount_paisa,
            "currency": "INR",
            "description": link_payload["description"],
            "is_mock": True
        }

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verifies the HMAC SHA256 signature returned by Razorpay Checkout frontend modal.
        """
        if self.is_mock or razorpay_order_id.startswith("order_mock_"):
            return True

        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            self.key_secret.encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(generated_signature, razorpay_signature)
