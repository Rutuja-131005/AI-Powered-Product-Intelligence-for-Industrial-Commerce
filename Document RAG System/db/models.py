"""
SQLAlchemy Database Models for Product Intelligence
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class EnrichmentJob(Base):
    __tablename__ = "enrichment_jobs"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(32), default="QUEUED", index=True)  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    products = relationship("ProductRecord", back_populates="job", cascade="all, delete-orphan")

class ProductRecord(Base):
    __tablename__ = "product_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), ForeignKey("enrichment_jobs.id"), index=True)
    row_index = Column(Integer, nullable=False)
    
    # Input columns
    mfg_part_num = Column(String(255), index=True)
    part_desc = Column(Text)
    e1_brand = Column(String(255))
    unilog_brand = Column(String(255))
    dib_brand = Column(String(255))
    part_manuf = Column(String(255))

    # Canonical Resolution
    canonical_part_number = Column(String(255), index=True)
    normalized_part_number = Column(String(255), index=True)
    resolved_brand = Column(String(255), index=True)
    product_title = Column(Text)

    # Evaluation Metadata
    overall_confidence_score = Column(Float, default=0.0)
    validation_status = Column(String(32), default="PENDING")  # VERIFIED, PARTIAL, NEEDS_REVIEW, FAILED
    review_status = Column(String(32), default="PENDING")      # PENDING, APPROVED, REJECTED, EDITED
    
    # Full 252-Column Payload (JSON formatted dictionary)
    payload_json = Column(JSON, nullable=False)
    provenance_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    job = relationship("EnrichmentJob", back_populates="products")
