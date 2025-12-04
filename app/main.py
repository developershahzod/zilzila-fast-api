from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.db.database import engine
from app.models import earthquake
import time
import logging
from sqlalchemy import exc

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to connect to the database with retries
max_retries = 5
retries = 0
while retries < max_retries:
    try:
        # Create database tables
        earthquake.Base.metadata.create_all(bind=engine)
        logger.info("Successfully connected to the database")
        break
    except exc.OperationalError as e:
        retries += 1
        logger.warning(f"Database connection failed (attempt {retries}/{max_retries}): {e}")
        if retries < max_retries:
            time.sleep(5)  # Wait 5 seconds before retrying
        else:
            logger.error("Failed to connect to the database after multiple attempts")
            raise

app = FastAPI(
    title="SMRM Earthquake API",
    description="API for earthquake data from SMRM",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SMRM Earthquake API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
