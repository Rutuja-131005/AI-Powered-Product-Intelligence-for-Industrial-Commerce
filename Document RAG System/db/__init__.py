from .database import Base, engine, SessionLocal, get_db
from .models import EnrichmentJob, ProductRecord

# Create tables
Base.metadata.create_all(bind=engine)
