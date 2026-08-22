from .database import Base, engine, SessionLocal, get_db
from .models import (
    Job, Product, ProductAttribute, Source, Evidence,
    ValidationResult, Review, ProductAsset
)
from .schemas import (
    JobCreateResponse, JobStatusResponse, ProductIdentity,
    ProductAttribute as PydanticProductAttribute, Evidence as PydanticEvidence,
    Source as PydanticSource, ValidationResult as PydanticValidationResult,
    ReviewAction, ProductIntelligence, ExportValidationResult
)

# Initialize all database tables
Base.metadata.create_all(bind=engine)
