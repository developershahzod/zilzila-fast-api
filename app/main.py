from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.db.database import engine
from app.models import earthquake
from app.scheduler import start_scheduler, get_sync_status
from app.arcgis_sync_scheduler import start_arcgis_scheduler, get_arcgis_sync_status
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

@app.on_event("startup")
async def startup_event():
    """
    Start background tasks on application startup
    """
    logger.info("Starting application...")
    start_scheduler()  # External API → Database sync (every 10 minutes)
    start_arcgis_scheduler()  # Database → ArcGIS sync (every 10 minutes)
    logger.info("Application started - BOTH schedulers ENABLED (every 10 minutes)")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SMRM Earthquake API",
        "docs": "/docs",
        "redoc": "/redoc",
        "external_api_sync": "ENABLED - Syncs from api.smrm.uz every 10 minutes",
        "arcgis_sync": "ENABLED - Syncs to ArcGIS every 10 minutes (needs valid credentials)",
        "manual_sync": "Available at: POST /api/earthquakes/sync"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint with scheduler status
    """
    sync_status = get_sync_status()
    arcgis_status = get_arcgis_sync_status()
    return {
        "status": "healthy",
        "external_api_sync": {
            "enabled": True,
            "interval": "10 minutes",
            "source": "api.smrm.uz",
            "destination": "PostgreSQL Database",
            "is_syncing": sync_status["is_syncing"],
            "last_sync_time": sync_status["last_sync_time"]
        },
        "arcgis_sync": {
            "enabled": True,
            "interval": "10 minutes",
            "source": "PostgreSQL Database",
            "destination": "ArcGIS Feature Server",
            "is_syncing": arcgis_status["is_syncing"],
            "last_sync_time": arcgis_status["last_sync_time"],
            "stats": arcgis_status["stats"]
        }
    }

@app.get("/sync-status")
def sync_status():
    """
    Get detailed sync status
    """
    status = get_sync_status()
    arcgis_status = get_arcgis_sync_status()
    return {
        "internal_scheduler": {
            "enabled": False,
            "interval_seconds": 0,
            "interval_minutes": 0,
            "status": "DISABLED"
        },
        "arcgis_scheduler": {
            "enabled": True,
            "interval_seconds": 600,
            "interval_minutes": 10,
            "status": "ACTIVE",
            "target": "https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer"
        },
        "current_sync": {
            "internal_is_running": status["is_syncing"],
            "internal_last_completed": status["last_sync_time"],
            "arcgis_is_running": arcgis_status["is_syncing"],
            "arcgis_last_completed": arcgis_status["last_sync_time"]
        },
        "arcgis_stats": arcgis_status["stats"],
        "manual_sync": {
            "endpoint": "POST /api/earthquakes/sync",
            "duplicate_prevention": "enabled",
            "lock_based": True,
            "resource_management": "active"
        }
    }

@app.get("/arcgis-sync-status")
def arcgis_sync_status_endpoint():
    """
    Get detailed ArcGIS sync status
    """
    status = get_arcgis_sync_status()
    return {
        "scheduler": {
            "enabled": True,
            "interval": "10 minutes",
            "target": "https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer"
        },
        "current_status": {
            "is_syncing": status["is_syncing"],
            "last_sync_time": status["last_sync_time"]
        },
        "statistics": status["stats"],
        "features": {
            "duplicate_prevention": "enabled",
            "check_by_id": True,
            "check_by_location": True,
            "batch_size": 100
        }
    }
