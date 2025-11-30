from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.models import Base
import os


# Database URL (SQLite file)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./research_assistant.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database - create all tables"""
    print("🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")

def get_db():
    """Dependency for FastAPI - provides database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()