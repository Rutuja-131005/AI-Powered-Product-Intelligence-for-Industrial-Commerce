"""
SQLAlchemy Relational Models for AI Product Intelligence
Implements 8 core relational entities:
1. jobs
2. products
3. product_attributes (1..50)
4. sources
5. evidence
6. validation_results
7. reviews
8. product_assets
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    success_rows = Column(Integer, default=0)
    review_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(String(32), default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    products = relationship("Product", back_populates="job", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), ForeignKey("jobs.id"), index=True)
    input_row_number = Column(Integer, nullable=False)
    product_key = Column(String(255), index=True)
    part_number = Column(String(255), index=True)
    part_description = Column(Text)
    manufacturer_raw = Column(String(255))
    manufacturer_normalized = Column(String(255), index=True)
    brand = Column(String(255), index=True)
    manufacturer_part_number = Column(String(255), index=True)
    product_name = Column(Text)
    category_path = Column(String(512))
    identity_confidence = Column(Float, default=0.0)
    overall_confidence = Column(Float, default=0.0)
    validation_status = Column(String(32), default="PENDING", index=True)  # VERIFIED, PARTIAL, NEEDS_REVIEW, FAILED
    review_status = Column(String(32), default="PENDING", index=True)      # PENDING, APPROVED, REJECTED, EDITED
    
    # 252-Column Payload Storage
    canonical_payload = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="products")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="product", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="product", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    assets = relationship("ProductAsset", back_populates="product", cascade="all, delete-orphan")

class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    attribute_index = Column(Integer, nullable=False)  # 1..50
    label = Column(String(255), nullable=False)
    value = Column(Text)
    uom = Column(String(64))
    normalized_value = Column(Text)
    normalized_uom = Column(String(64))
    source_type = Column(String(64), default="DESCRIPTIVE_EXTRACTION")
    confidence = Column(Float, default=0.0)
    validation_status = Column(String(32), default="VERIFIED")

    product = relationship("Product", back_populates="attributes")

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    url = Column(Text, nullable=False)
    domain = Column(String(255), index=True)
    title = Column(String(255))
    source_type = Column(String(64))  # MANUFACTURER_EXACT, SPEC_SHEET, MANUAL, DISTRIBUTOR
    trust_score = Column(Float, default=0.90)
    http_status = Column(Integer, default=200)
    content_hash = Column(String(64))
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="sources")
    evidence_items = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    attribute_id = Column(Integer, ForeignKey("product_attributes.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    page_number = Column(Integer, nullable=True)
    section = Column(String(255), nullable=True)
    chunk_id = Column(String(64), nullable=True)
    evidence_text = Column(Text, nullable=False)
    relevance_score = Column(Float, default=0.85)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="evidence")
    source = relationship("Source", back_populates="evidence_items")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    field_name = Column(String(255), nullable=False)
    rule_code = Column(String(64), nullable=False)  # SCHEMA_CHECK, UOM_CHECK, EVIDENCE_GROUNDING
    status = Column(String(32), default="PASS")     # PASS, REVIEW, FAIL
    severity = Column(String(32), default="INFO")   # INFO, WARNING, ERROR
    message = Column(Text)
    expected_value = Column(Text, nullable=True)
    actual_value = Column(Text, nullable=True)
    source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="validation_results")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    field_name = Column(String(255), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    action = Column(String(32), default="EDIT")  # APPROVE, REJECT, EDIT
    reviewer = Column(String(255), default="data_manager")
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="reviews")

class ProductAsset(Base):
    __tablename__ = "product_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    asset_type = Column(String(64))  # PRIMARY_IMAGE, 3D_CAD, SPEC_SHEET, MANUAL, SDS
    url_or_path = Column(Text, nullable=False)
    filename = Column(String(255))
    source_id = Column(Integer, nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="assets")
