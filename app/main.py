from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.db import init_db
from app.api.auth_routes import router as auth_router
from app.api.research_routes import router as research_router
import warnings
import logging
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Research Assistant API...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="AI Research Assistant with Authentication & Database",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(research_router)

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Multi-Agent Research Assistant API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "User Authentication (JWT)",
            "Multi-Agent Research System",
            "Research History Storage",
            "SQLite Database"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}