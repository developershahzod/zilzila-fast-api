from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.db.database import engine
from app.models import earthquake
from app.scheduler import start_scheduler, stop_scheduler, get_sync_status
from app.arcgis_sync_scheduler import (
    start_arcgis_scheduler,
    stop_arcgis_scheduler,
    get_arcgis_sync_status,
    sync_to_arcgis_task,
    reset_arcgis_error_stats,
    get_arcgis_token,
)
import time
import logging
from datetime import datetime
from sqlalchemy import exc

import os

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

EXTERNAL_API_SCHEDULER_ENABLED = os.getenv("EXTERNAL_API_SCHEDULER_ENABLED", "false").strip().lower() in {"1", "true", "yes", "y", "on"}
ARCGIS_SCHEDULER_ENABLED = os.getenv("ARCGIS_SCHEDULER_ENABLED", "false").strip().lower() in {"1", "true", "yes", "y", "on"}

@app.on_event("startup")
async def startup_event():
    """
    Start background tasks on application startup
    """
    logger.info("Starting application...")
    if EXTERNAL_API_SCHEDULER_ENABLED:
        start_scheduler()  # External API → Database sync (every 10 minutes)
        logger.info("External API scheduler ENABLED")
    else:
        logger.info("External API scheduler DISABLED")

    if ARCGIS_SCHEDULER_ENABLED:
        start_arcgis_scheduler()  # Database → ArcGIS sync (every 10 minutes)
        logger.info("ArcGIS scheduler ENABLED")
    else:
        logger.info("ArcGIS scheduler DISABLED")

    logger.info("Application started")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SMRM Earthquake API",
        "docs": "/docs",
        "redoc": "/redoc",
        "external_api_sync": "ENABLED - Syncs from api.smrm.uz every 10 minutes" if EXTERNAL_API_SCHEDULER_ENABLED else "DISABLED",
        "arcgis_sync": "ENABLED - Syncs to ArcGIS every 10 minutes with auto-retry" if ARCGIS_SCHEDULER_ENABLED else "DISABLED",
        "api_endpoints": {
            "check_token": "GET /arcgis-token-check - Test ArcGIS token generation",
            "start_sync": "POST /arcgis-sync-start - Manually start ArcGIS sync",
            "sync_status": "GET /arcgis-sync-status - Check ArcGIS sync status",
            "manual_sync": "POST /api/earthquakes/sync - Sync from external API"
        }
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
            "enabled": sync_status.get("enabled", False),
            "interval": "10 minutes",
            "source": "api.smrm.uz",
            "destination": "PostgreSQL Database",
            "is_syncing": sync_status["is_syncing"],
            "last_sync_time": sync_status["last_sync_time"]
        },
        "arcgis_sync": {
            "enabled": arcgis_status.get("enabled", False),
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
            "enabled": status.get("enabled", False),
            "interval_seconds": 600 if status.get("enabled", False) else 0,
            "interval_minutes": 10 if status.get("enabled", False) else 0,
            "status": "ACTIVE" if status.get("enabled", False) else "DISABLED"
        },
        "arcgis_scheduler": {
            "enabled": arcgis_status.get("enabled", False),
            "interval_seconds": 600 if arcgis_status.get("enabled", False) else 0,
            "interval_minutes": 10 if arcgis_status.get("enabled", False) else 0,
            "status": "ACTIVE" if arcgis_status.get("enabled", False) else "DISABLED",
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
            "enabled": status.get("enabled", False),
            "interval": "10 minutes" if status.get("enabled", False) else "disabled",
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


@app.post("/scheduler/external/enable")
async def enable_external_scheduler():
    start_scheduler()
    return {"status": "success", "external_scheduler": get_sync_status()}


@app.post("/scheduler/external/disable")
async def disable_external_scheduler():
    await stop_scheduler()
    return {"status": "success", "external_scheduler": get_sync_status()}


@app.post("/scheduler/arcgis/enable")
async def enable_arcgis_scheduler():
    start_arcgis_scheduler()
    return {"status": "success", "arcgis_scheduler": get_arcgis_sync_status()}


@app.post("/scheduler/arcgis/disable")
async def disable_arcgis_scheduler():
    await stop_arcgis_scheduler()
    return {"status": "success", "arcgis_scheduler": get_arcgis_sync_status()}


@app.get("/scheduler/status")
def scheduler_status():
    return {
        "external_scheduler": get_sync_status(),
        "arcgis_scheduler": get_arcgis_sync_status(),
    }

@app.get("/arcgis-token-check")
def check_arcgis_token():
    """
    Check ArcGIS token generation
    Tests if token can be generated with current credentials and endpoint
    Returns token info without exposing the full token
    """
    try:
        logger.info("🔑 Testing ArcGIS token generation...")
        
        token = get_arcgis_token()
        
        if token:
            return {
                "status": "success",
                "message": "Token generated successfully",
                "token_info": {
                    "length": len(token),
                    "preview": f"{token[:30]}..." if len(token) > 30 else token,
                    "endpoint": "https://gis.uzspace.uz/uzspace/sharing/rest/generateToken",
                    "client_type": "referer",
                    "expiration": "20160 minutes (14 days)"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Failed to generate token",
                "details": "Check application logs for detailed error information",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"❌ Token check failed: {e}")
        return {
            "status": "error",
            "message": f"Token check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/arcgis-sync-start")
async def start_arcgis_sync():
    """
    Start ArcGIS sync manually
    This will sync all earthquakes from database to ArcGIS Feature Server
    Includes automatic retry logic for failed batches
    """
    status = get_arcgis_sync_status()
    if status["is_syncing"]:
        return {
            "status": "error",
            "message": "ArcGIS sync is already in progress",
            "is_syncing": True,
            "last_sync_time": status["last_sync_time"]
        }
    
    try:
        logger.info("🚀 Starting ArcGIS sync via API...")
        
        # Reset error stats before starting new sync
        reset_arcgis_error_stats()
        
        # Trigger sync with new token
        await sync_to_arcgis_task()
        
        # Get updated status
        updated_status = get_arcgis_sync_status()
        
        return {
            "status": "success",
            "message": "ArcGIS sync completed",
            "statistics": updated_status["stats"],
            "last_sync_time": updated_status["last_sync_time"],
            "features": {
                "retry_enabled": True,
                "max_retries": 3,
                "batch_size": 100
            }
        }
    except Exception as e:
        logger.error(f"❌ ArcGIS sync failed: {e}")
        return {
            "status": "error",
            "message": f"ArcGIS sync failed: {str(e)}"
        }

@app.post("/arcgis-sync-manual")
async def manual_arcgis_sync():
    """
    Manually trigger ArcGIS sync with new token (Legacy endpoint - use /arcgis-sync-start instead)
    This will sync all earthquakes from database to ArcGIS Feature Server
    Uses the updated token configuration with correct endpoint and credentials
    """
    return await start_arcgis_sync()
