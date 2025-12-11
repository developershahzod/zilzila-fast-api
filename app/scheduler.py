"""
Background scheduler for automatic earthquake data synchronization
Runs sync task every 10 minutes with duplicate prevention and resource management
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.earthquake_service import EarthquakeService
from app.services.api_service import ApiService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global lock to prevent concurrent sync operations
_sync_lock = asyncio.Lock()
_is_syncing = False
_last_sync_time = None


async def sync_earthquakes_task():
    """
    Sync earthquakes from external API with duplicate prevention
    This task runs every 10 minutes
    """
    global _is_syncing, _last_sync_time
    
    # Check if sync is already running
    if _is_syncing:
        logger.warning("⚠️ Sync already in progress, skipping this run")
        return
    
    # Acquire lock to prevent concurrent execution
    async with _sync_lock:
        _is_syncing = True
        start_time = datetime.now()
        logger.info(f"[{start_time}] Starting automatic earthquake sync from external API...")
        
        db: Session = None
        try:
            # Create database session
            db = SessionLocal()
            
            # Fetch data from external API (page 1, 100 records per page)
            api_data = await ApiService.fetch_earthquakes(page=1, per_page=100)
            
            # Extract earthquake data from the result object
            result = api_data.get("result", {})
            earthquakes_data = result.get("data", [])
            
            if earthquakes_data:
                # Save to database
                earthquakes, skipped = EarthquakeService.bulk_create_earthquakes(db, earthquakes_data)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(
                    f"✅ External API sync completed in {duration:.2f}s: "
                    f"{len(earthquakes)} synced, {skipped} skipped, "
                    f"{len(earthquakes_data)} total processed"
                )
                _last_sync_time = end_time
            else:
                logger.info("No new earthquakes from external API")
                _last_sync_time = datetime.now()
                
        except Exception as e:
            logger.error(f"❌ External API sync failed: {str(e)}")
        finally:
            # Always close database connection
            if db:
                db.close()
            _is_syncing = False


async def run_scheduler():
    """
    Run the sync task every 10 minutes with resource management
    """
    logger.info("🚀 External API sync scheduler started (runs every 10 minutes)")
    logger.info("📊 Resource management: Lock-based duplicate prevention enabled")
    
    # Run first sync after 30 seconds (give app time to fully start)
    await asyncio.sleep(30)
    
    while True:
        try:
            await sync_earthquakes_task()
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
        
        # Wait 10 minutes (600 seconds)
        logger.info("⏰ Next external API sync in 10 minutes...")
        await asyncio.sleep(600)


def start_scheduler():
    """
    Start the background scheduler for External API → Database sync
    """
    asyncio.create_task(run_scheduler())
    logger.info("✅ External API sync scheduler ENABLED")


def get_sync_status():
    """
    Get current sync status
    """
    return {
        "is_syncing": _is_syncing,
        "last_sync_time": _last_sync_time.isoformat() if _last_sync_time else None
    }
