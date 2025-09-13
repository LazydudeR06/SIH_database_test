from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Base class for ORM models
Base = declarative_base()

# Try full DATABASE_URL first
DATABASE_URL = os.getenv("DATABASE_URL")

# Or build it from parts if not provided
if not DATABASE_URL:
    user = os.getenv("DATABASE_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")
    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME", "postgres")
    
    # Check if we have the required credentials
    if not user or not password:
        print("Warning: Missing DATABASE_USERNAME or DATABASE_PASSWORD")
        print("Available environment variables:")
        for key in os.environ:
            if "DATABASE" in key:
                print(f"  {key} = {os.environ[key]}")
        
        # For development, you can use a default local database
        DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/postgres"
        print(f"Using default DATABASE_URL: {DATABASE_URL}")
    else:
        DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

print("Using DATABASE_URL =", DATABASE_URL)

# Create engine
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    # Test the connection
    with engine.connect() as conn:
        print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
    print("Please check your database credentials and ensure PostgreSQL is running.")
    raise

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility for creating tables
def create_tables():
    Base.metadata.create_all(bind=engine)