# ArcGIS Sync Error Fix - 143 Batches Failed

## Problem
```json
{
  "arcgis_stats": {
    "total_sent": 0,
    "total_skipped": 0,
    "last_error": "143 batches failed"
  }
}
```

## Root Cause
The previous sync attempts failed because:
1. **Wrong endpoint**: Was using `/uzspacesrvr/tokens/generateToken` (returns 401)
2. **Wrong credentials**: Was using `farhodmf` / `AQ!SW@de3?` (invalid)
3. **Wrong client type**: Was using `client=requestip` (not supported properly)
4. **Missing referer**: Required for the working endpoint

## ✅ Solution Applied

### 1. Fixed Token Generation
Updated to use the **correct working endpoint**:
```
https://gis.uzspace.uz/uzspace/sharing/rest/generateToken
```

### 2. Corrected Credentials
```python
ARCGIS_USERNAME = "zilzila"
ARCGIS_PASSWORD = "zilzila@6739space"
```

### 3. Updated Parameters
```python
{
    "username": "zilzila",
    "password": "zilzila@6739space",
    "client": "referer",
    "referer": "https://api-zilzila.spacemc.uz/",
    "expiration": 20160,  # 14 days
    "f": "json"
}
```

### 4. Added Browser-Like Headers
```python
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,...",
    "Accept-Language": "ru-RU,ru;q=0.9,en-GB;q=0.8,...",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
```

## 🔧 New Features Added

### 1. Manual Sync Endpoint
**Endpoint**: `POST /arcgis-sync-manual`

**Purpose**: Manually trigger ArcGIS sync with the new token configuration

**Usage**:
```bash
curl -X POST http://localhost:8005/arcgis-sync-manual
```

**Response**:
```json
{
  "status": "success",
  "message": "ArcGIS sync completed",
  "statistics": {
    "total_sent": 1430,
    "total_skipped": 0,
    "last_error": null
  },
  "last_sync_time": "2025-12-12T15:50:00.123456"
}
```

### 2. Error Stats Reset Function
Automatically clears previous error stats before starting a new sync attempt.

## 📋 How to Fix the Current Error

### Step 1: Restart the Application
The code changes have been applied. Restart your FastAPI application:

```bash
# If running with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

# Or if using docker
docker-compose restart
```

### Step 2: Trigger Manual Sync
Once the app is running, trigger a manual sync to retry with the new configuration:

```bash
curl -X POST http://localhost:8005/arcgis-sync-manual
```

Or visit in your browser:
```
http://localhost:8005/docs
```
Then find the `POST /arcgis-sync-manual` endpoint and click "Try it out" → "Execute"

### Step 3: Monitor the Sync
Check the sync status:

```bash
curl http://localhost:8005/arcgis-sync-status
```

Expected output after successful sync:
```json
{
  "scheduler": {
    "enabled": true,
    "interval": "10 minutes",
    "target": "https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer"
  },
  "current_status": {
    "is_syncing": false,
    "last_sync_time": "2025-12-12T15:50:00.123456"
  },
  "statistics": {
    "total_sent": 1430,
    "total_skipped": 0,
    "last_error": null
  }
}
```

### Step 4: Check Application Logs
Monitor the logs for detailed information:

```bash
# Look for these log messages:
🔑 Attempting ArcGIS Portal token authentication...
🔑 Trying: https://gis.uzspace.uz/uzspace/sharing/rest/generateToken
✅ Token obtained from: https://gis.uzspace.uz/uzspace/sharing/rest/generateToken
📤 Sending X features to ArcGIS...
✅ Successfully sent X/X features to ArcGIS
```

## 🎯 What Changed in the Code

### Files Modified:
1. **`app/arcgis_sync_scheduler.py`**
   - Updated token endpoint to `/uzspace/sharing/rest/generateToken`
   - Changed credentials back to `zilzila` / `zilzila@6739space`
   - Changed client type to `referer` with proper referer URL
   - Extended token expiration to 14 days (20160 minutes)
   - Added browser-like headers for better compatibility
   - Added `reset_arcgis_error_stats()` function

2. **`app/main.py`**
   - Added `POST /arcgis-sync-manual` endpoint
   - Imported `sync_to_arcgis_task` and `reset_arcgis_error_stats`
   - Added automatic error stats reset before manual sync

## ✅ Verification

### Test Token Generation
```bash
./test_token_final.sh
```

Expected output:
```json
{
    "token": "ENZv8H3YrJnY9XsyFSM5iPi1KE7zIDNoyOzlI...",
    "expires": 1766746139626,
    "ssl": true
}
```

### Test Manual Sync
```bash
curl -X POST http://localhost:8005/arcgis-sync-manual
```

## 🔄 Automatic Sync

After the manual sync succeeds, the automatic scheduler will continue to run every 10 minutes with the new configuration. No further action needed.

## 📊 Expected Results

After successful sync:
- **total_sent**: Number of new features sent to ArcGIS
- **total_skipped**: Number of duplicates skipped
- **last_error**: `null` (no errors)

## 🆘 Troubleshooting

### If sync still fails:

1. **Check token generation**:
   ```bash
   ./test_token_final.sh
   ```

2. **Check application logs** for detailed error messages

3. **Verify ArcGIS server is accessible**:
   ```bash
   curl -k https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer/2
   ```

4. **Check database connection** - ensure earthquakes exist in database

5. **Verify user permissions** - ensure `zilzila` user has write access to the feature layer

## 📝 Summary

✅ Token generation endpoint fixed  
✅ Credentials corrected  
✅ Client type and referer configured  
✅ Token expiration extended to 14 days  
✅ Manual sync endpoint added  
✅ Error stats reset functionality added  
✅ Ready to retry sync with new configuration

**Next Action**: Restart the application and trigger manual sync using `POST /arcgis-sync-manual`
