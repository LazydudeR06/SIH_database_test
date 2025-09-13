from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Base class for ORM models
Base = declarative_base()

# Database URL from Supabase (use service_role password if needed for backend)
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DATABASE_USERNAME')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}:"
    f"{os.getenv('DATABASE_PORT')}/"
    f"{os.getenv('DATABASE_NAME')}"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes
def get_db():
    """
    Provides a SQLAlchemy session for dependency injection in FastAPI.
    Ensures session closes after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Utility for creating tables
def create_tables():
    Base.metadata.create_all(bind=engine)