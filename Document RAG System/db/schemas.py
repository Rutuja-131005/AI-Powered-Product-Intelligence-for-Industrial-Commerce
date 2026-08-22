"""
Pydantic v2 Schemas for Product Intelligence REST API and Canonical Objects
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# --- Pydantic API Models ---

class JobCreateResponse(BaseModel):
    job_id: str
    filename: str
    status: str
    total_rows: int
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    filename: str
    status: str
    total_rows: int
    processed_rows: int
    success_rows: int
    review_rows: int
    failed_rows: int
    progress_percent: float
    elapsed_seconds: float
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ProductIdentity(BaseModel):
    part_number: str
    manufacturer: str
    brand: str
    manufacturer_part_number: str
    alternate_part_number: Optional[str] = None
    canonical_key: Optional[str] = None
    confidence: float = 1.0

class ProductAttribute(BaseModel):
    attribute_index: int = Field(ge=1, le=50)
    label: str
    value: Optional[str] = ""
    uom: Optional[str] = ""
    normalized_value: Optional[str] = ""
    normalized_uom: Optional[str] = ""
    confidence: float = 0.0
    status: str = "VERIFIED"

class Source(BaseModel):
    id: Optional[int] = None
    url: str
    domain: Optional[str] = ""
    title: Optional[str] = ""
    source_type: str = "MANUFACTURER_PORTAL"
    trust_score: float = 0.90
    content_hash: Optional[str] = None

class Evidence(BaseModel):
    id: Optional[int] = None
    source_id: Optional[int] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: Optional[str] = None
    evidence_text: str
    relevance_score: float = 0.85

class ValidationResult(BaseModel):
    field_name: str
    rule_code: str
    status: str = "PASS"  # PASS, REVIEW, FAIL
    severity: str = "INFO"
    message: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None

class ReviewAction(BaseModel):
    field_name: str
    new_value: str
    action: str = "EDIT"  # APPROVE, REJECT, EDIT
    reviewer: str = "data_manager"
    reason: Optional[str] = None

class ProductIntelligence(BaseModel):
    product_key: str
    identity: ProductIdentity
    taxonomy: Dict[str, Any] = {}
    content: Dict[str, Any] = {}
    attributes: List[ProductAttribute] = []
    commercial: Dict[str, Any] = {}
    dimensions: Dict[str, Any] = {}
    assets: List[Dict[str, Any]] = []
    sources: List[Source] = []
    validation: List[ValidationResult] = []
    overall_confidence: float = 0.0
    validation_status: str = "PENDING"
    review_status: str = "PENDING"

class ExportValidationResult(BaseModel):
    is_valid: bool
    expected_headers_count: int = 252
    actual_headers_count: int = 252
    total_rows: int
    errors: List[str] = []
