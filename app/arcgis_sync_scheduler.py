"""
ArcGIS Feature Server Sync Scheduler
Syncs earthquake data to ArcGIS every 10 minutes with duplicate prevention
"""

import asyncio
import logging
import requests
import urllib3
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import SessionLocal
from app.models.earthquake import Earthquake

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ArcGIS Configuration
ARCGIS_BASE_URL = "https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer"
ARCGIS_LAYER_ID = 2  # Layer ID for the feature layer (changed from 0 to 2)
ARCGIS_USERNAME = "zilzila"
ARCGIS_PASSWORD = "zilzila@6739space"

# OAuth2 Configuration (if using OAuth2 instead of username/password)
ARCGIS_CLIENT_ID = "zilzila"  # Update with actual client_id if different
ARCGIS_CLIENT_SECRET = "zilzila@6739space"  # Update with actual client_secret if different

# Manual token (if token generation fails, use this as fallback)
# Token expires after some time, need to regenerate from portal
ARCGIS_MANUAL_TOKEN = "IVxIfrcp1UB6KPqjQhW9NHHezLTqbm233z2Ep3ACPs6Lwn_MjfEL7horw61Z4W8i0eEC55NjxNfg79UCMN26jY_exZj8VNjs0FspxDap_Fa2ANbiY-O9WJo3KULR-JzB6qfeey1aU2lYWoDPDLhmPW7eQiY3NWI7VWIlaDkuYmNFIa9qSLUZGt46o9BeLx6ojgYsqXRhL3iOgIDfBxB8uSEoi6Uk1Jy5PkiQ3IrK3v4Up8tOB8JJ3iCdmYPChw75"

# Global lock to prevent concurrent sync operations
_sync_lock = asyncio.Lock()
_is_syncing = False
_last_sync_time = None
_sync_stats = {
    "total_sent": 0,
    "total_skipped": 0,
    "last_error": None
}


def get_arcgis_token() -> str:
    """
    Get authentication token from ArcGIS - Following official documentation
    """
    
    # Method 1: Standard ArcGIS Server Token Generation (from documentation)
    # POST /arcgis/tokens/generateToken
    logger.info("🔑 Attempting ArcGIS Server token authentication...")
    
    token_urls = [
        "https://gis.uzspace.uz/arcgis/tokens/generateToken",
        "https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken",
        "https://gis.uzspace.uz/server/tokens/generateToken",
    ]
    
    # According to docs: username, password, client, referer (if client=referer), expiration, f
    token_params = {
        "username": ARCGIS_USERNAME,
        "password": ARCGIS_PASSWORD,
        "client": "requestip",  # or "referer" or "ip"
        "expiration": 60,  # 60 minutes
        "f": "json"
    }
    
    for url in token_urls:
        try:
            logger.info(f"🔑 Trying: {url}")
            logger.info(f"📝 Parameters: username={ARCGIS_USERNAME}, client=requestip, expiration=60")
            
            # Must use POST with application/x-www-form-urlencoded
            response = requests.post(
                url, 
                data=token_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10, 
                verify=False
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📄 Response: {result}")
                
                if "token" in result:
                    logger.info(f"✅ Token obtained from: {url}")
                    logger.info(f"✅ Expires: {result.get('expires', 'unknown')}")
                    logger.info(f"✅ Token (first 30 chars): {result['token'][:30]}...")
                    return result["token"]
                elif "error" in result:
                    logger.error(f"❌ Token error: {result['error']}")
            else:
                logger.warning(f"⚠️ HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed {url}: {e}")
            continue
    
    # Method 2: Try with referer client type
    logger.info("🔑 Attempting with referer client type...")
    token_params_referer = {
        "username": ARCGIS_USERNAME,
        "password": ARCGIS_PASSWORD,
        "client": "referer",
        "referer": "https://gis.uzspace.uz",
        "expiration": 60,
        "f": "json"
    }
    
    for url in token_urls:
        try:
            logger.info(f"🔑 Trying with referer: {url}")
            response = requests.post(
                url,
                data=token_params_referer,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if "token" in result:
                    logger.info(f"✅ Token obtained with referer from: {url}")
                    return result["token"]
                    
        except Exception as e:
            logger.debug(f"Failed {url}: {e}")
            continue
    
    # Method 3: Try OAuth2 (if server supports it)
    logger.info("🔑 Attempting OAuth2 authentication...")
    oauth2_urls = [
        "https://gis.uzspace.uz/portal/sharing/rest/oauth2/token",
        "https://gis.uzspace.uz/uzspacesrvr/sharing/rest/oauth2/token",
    ]
    
    oauth2_params = {
        "f": "json",
        "client_id": ARCGIS_CLIENT_ID,
        "client_secret": ARCGIS_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    for url in oauth2_urls:
        try:
            response = requests.post(url, data=oauth2_params, timeout=10, verify=False)
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result:
                    logger.info(f"✅ OAuth2 token obtained from: {url}")
                    return result["access_token"]
        except:
            continue
    
    logger.error("❌ All authentication methods failed")
    logger.warning("⚠️ Falling back to manual token...")
    
    # Fallback to manual token if available
    if ARCGIS_MANUAL_TOKEN:
        logger.info("✅ Using manual token from configuration")
        logger.info(f"✅ Token (first 30 chars): {ARCGIS_MANUAL_TOKEN[:30]}...")
        return ARCGIS_MANUAL_TOKEN
    
    logger.error("❌ No manual token available")
    logger.error("❌ Please verify:")
    logger.error("   1. Username and password are correct")
    logger.error("   2. User has permissions to generate tokens")
    logger.error("   3. Token generation endpoint is accessible")
    return None


def get_existing_arcgis_features(token: str) -> List[Dict]:
    """
    Get existing features from ArcGIS to check for duplicates
    """
    query_url = f"{ARCGIS_BASE_URL}/{ARCGIS_LAYER_ID}/query"
    
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "false",
        "f": "json"
    }
    
    # Add token only if available
    if token:
        params["token"] = token
    
    try:
        logger.info(f"📊 Querying existing features from ArcGIS...")
        response = requests.get(query_url, params=params, timeout=30, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            
            if "features" in result:
                logger.info(f"📊 Found {len(result['features'])} existing features in ArcGIS")
                return result["features"]
            elif "error" in result:
                error_msg = result.get("error", {})
                if error_msg.get("code") == 499:  # Token required
                    logger.warning("⚠️ ArcGIS requires authentication, cannot check duplicates")
                else:
                    logger.error(f"❌ Query error: {error_msg}")
                return []
            else:
                logger.warning("⚠️ No features found in ArcGIS")
                return []
        else:
            logger.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error querying ArcGIS features: {e}")
        return []


def convert_to_arcgis_feature(earthquake: Earthquake) -> Dict:
    """
    Convert earthquake model to ArcGIS feature format
    Mapping to match ArcGIS field names (some are truncated to 10 chars)
    """
    return {
        "geometry": {
            "x": float(earthquake.longitude),
            "y": float(earthquake.latitude),
            "spatialReference": {"wkid": 4326}
        },
        "attributes": {
            # Map database fields to ArcGIS field names
            "earthquake": earthquake.earthquake_id,  # earthquake_id -> earthquake
            "date": earthquake.date,
            "time": earthquake.time,
            "latitude": float(earthquake.latitude),
            "longitude": float(earthquake.longitude),
            "depth": float(earthquake.depth) if earthquake.depth else None,
            "magnitude": float(earthquake.magnitude) if earthquake.magnitude else None,
            "magnitude_": earthquake.magnitude_type,  # magnitude_type -> magnitude_
            "epicenter": earthquake.epicenter,
            "epicenter_": earthquake.epicenter_ru,  # epicenter_ru -> epicenter_
            "epicenter1": earthquake.epicenter_en,  # epicenter_en -> epicenter1
            "color": earthquake.color,
            "descriptio": earthquake.description[:254] if earthquake.description else None,  # description -> descriptio (truncated)
            "is_percept": 1 if earthquake.is_perceptabily else 0,  # is_perceptabily -> is_percept (boolean to int)
            "created_at": earthquake.created_at.isoformat() if earthquake.created_at else None,
            "updated_at": earthquake.updated_at.isoformat() if earthquake.updated_at else None,
            "created_by": earthquake.created_by,
            "updated_by": earthquake.updated_by,
            "id": earthquake.id
        }
    }


def is_duplicate(earthquake: Earthquake, existing_features: List[Dict]) -> bool:
    """
    Check if earthquake already exists in ArcGIS
    Using ArcGIS field names: earthquake (not earthquake_id)
    """
    for feature in existing_features:
        attrs = feature.get("attributes", {})
        
        # Check by earthquake_id (mapped to 'earthquake' field in ArcGIS)
        if earthquake.earthquake_id and attrs.get("earthquake") == earthquake.earthquake_id:
            return True
        
        # Check by date, time, and location
        if (attrs.get("date") == earthquake.date and
            attrs.get("time") == earthquake.time and
            attrs.get("latitude") == float(earthquake.latitude) and
            attrs.get("longitude") == float(earthquake.longitude)):
            return True
    
    return False


def send_features_to_arcgis(features: List[Dict], token: str) -> bool:
    """
    Send features to ArcGIS Feature Server
    """
    if not features:
        logger.info("No features to send")
        return True
    
    add_url = f"{ARCGIS_BASE_URL}/{ARCGIS_LAYER_ID}/addFeatures"
    
    # Prepare data as form-encoded
    import json
    data = {
        "features": json.dumps(features),
        "f": "json",
        "token": token
    }
    
    try:
        logger.info(f"📤 Sending {len(features)} features to ArcGIS...")
        logger.info(f"🌐 URL: {add_url}")
        logger.info(f"📝 Sample feature: {json.dumps(features[0], indent=2)[:300]}...")
        
        response = requests.post(add_url, data=data, timeout=60, verify=False)
        
        logger.info(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"📄 Response body: {json.dumps(result, indent=2)[:500]}...")
            
            if "addResults" in result:
                success_count = sum(1 for r in result["addResults"] if r.get("success"))
                failed_count = len(features) - success_count
                
                # Log failed features details
                if failed_count > 0:
                    failed_results = [r for r in result["addResults"] if not r.get("success")]
                    logger.error(f"❌ Failed features details: {json.dumps(failed_results[:3], indent=2)}")
                    logger.warning(f"⚠️ Sent {success_count}/{len(features)} features ({failed_count} failed)")
                else:
                    logger.info(f"✅ Successfully sent {success_count}/{len(features)} features to ArcGIS")
                return success_count > 0
            elif "error" in result:
                logger.error(f"❌ Add features error: {json.dumps(result['error'], indent=2)}")
                return False
            else:
                logger.error(f"❌ Unexpected response: {json.dumps(result, indent=2)[:500]}")
                return False
        else:
            logger.error(f"❌ HTTP {response.status_code}")
            logger.error(f"❌ Response text: {response.text[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending features to ArcGIS: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False


async def sync_to_arcgis_task():
    """
    Sync ALL earthquakes from database to ArcGIS Feature Server with duplicate prevention
    """
    global _is_syncing, _last_sync_time, _sync_stats
    
    # Check if sync is already running
    if _is_syncing:
        logger.warning("⚠️ ArcGIS sync already in progress, skipping this run")
        return
    
    # Acquire lock to prevent concurrent execution
    async with _sync_lock:
        _is_syncing = True
        start_time = datetime.now()
        logger.info(f"[{start_time}] Starting ArcGIS sync from database...")
        
        db: Session = None
        try:
            # Get ArcGIS token
            token = get_arcgis_token()
            if not token:
                # If token fails, try without authentication (public access)
                logger.warning("⚠️ No token obtained, attempting public access...")
                token = ""
            
            # Get existing features from ArcGIS
            existing_features = get_existing_arcgis_features(token) if token else []
            
            # Get ALL earthquakes from database
            db = SessionLocal()
            earthquakes = db.query(Earthquake).order_by(desc(Earthquake.id)).all()
            logger.info(f"📊 Found {len(earthquakes)} total earthquakes in database")
            
            # Filter out duplicates
            new_features = []
            skipped = 0
            
            for earthquake in earthquakes:
                if is_duplicate(earthquake, existing_features):
                    skipped += 1
                else:
                    feature = convert_to_arcgis_feature(earthquake)
                    new_features.append(feature)
            
            logger.info(f"📤 Preparing to send {len(new_features)} new features (skipped {skipped} duplicates)")
            
            if len(new_features) == 0:
                logger.info("✅ All data already synced to ArcGIS, no new features to send")
                _last_sync_time = datetime.now()
                _sync_stats["total_sent"] = 0
                _sync_stats["total_skipped"] = skipped
                _sync_stats["last_error"] = None
                return
            
            # Send features to ArcGIS in batches of 100
            batch_size = 100
            total_sent = 0
            failed_batches = 0
            
            for i in range(0, len(new_features), batch_size):
                batch = new_features[i:i + batch_size]
                if send_features_to_arcgis(batch, token):
                    total_sent += len(batch)
                    logger.info(f"✅ Sent batch {i//batch_size + 1}/{(len(new_features)-1)//batch_size + 1} ({len(batch)} features)")
                else:
                    logger.error(f"❌ Failed to send batch {i//batch_size + 1}")
                    failed_batches += 1
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update stats
            _sync_stats["total_sent"] = total_sent
            _sync_stats["total_skipped"] = skipped
            _sync_stats["last_error"] = f"{failed_batches} batches failed" if failed_batches > 0 else None
            _last_sync_time = end_time
            
            logger.info(
                f"✅ ArcGIS sync completed in {duration:.2f}s: "
                f"{total_sent} sent, {skipped} skipped, {failed_batches} batches failed"
            )
            
        except Exception as e:
            logger.error(f"❌ ArcGIS sync failed: {str(e)}")
            _sync_stats["last_error"] = str(e)
        finally:
            # Always close database connection
            if db:
                db.close()
            _is_syncing = False


async def run_arcgis_scheduler():
    """
    Run the ArcGIS sync task every 10 minutes
    """
    logger.info("🚀 ArcGIS sync scheduler started (runs every 10 minutes)")
    logger.info("📊 Duplicate prevention: Enabled")
    logger.info(f"🌐 Target: {ARCGIS_BASE_URL}")
    
    # Run first sync after 30 seconds (give app time to fully start)
    await asyncio.sleep(30)
    
    while True:
        try:
            await sync_to_arcgis_task()
        except Exception as e:
            logger.error(f"Error in ArcGIS scheduler: {e}")
        
        # Wait 10 minutes (600 seconds)
        logger.info("⏰ Next ArcGIS sync in 10 minutes...")
        await asyncio.sleep(600)


def start_arcgis_scheduler():
    """
    Start the ArcGIS background scheduler
    """
    asyncio.create_task(run_arcgis_scheduler())


def get_arcgis_sync_status():
    """
    Get current ArcGIS sync status
    """
    return {
        "is_syncing": _is_syncing,
        "last_sync_time": _last_sync_time.isoformat() if _last_sync_time else None,
        "stats": _sync_stats
    }
