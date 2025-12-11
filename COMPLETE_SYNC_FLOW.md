# Complete Earthquake Data Sync Flow

## Overview

Complete data flow from External API → Database → ArcGIS with duplicate checking at each step.

## Flow Diagram

```
┌─────────────────────┐
│   External API      │
│  (api.smrm.uz)      │
└──────────┬──────────┘
           │
           │ Step 1: Sync to Database
           │ POST /api/earthquakes/sync
           │ ✅ Check duplicates in DB
           ▼
┌─────────────────────┐
│  Your Database      │
│  (PostgreSQL)       │
└──────────┬──────────┘
           │
           │ Step 2: Auto-sync to ArcGIS
           │ Every 10 minutes
           │ ✅ Check duplicates in ArcGIS
           ▼
┌─────────────────────┐
│   ArcGIS Server     │
│ (gis.uzspace.uz)    │
│ Layer 2             │
└─────────────────────┘
```

## Step 1: External API → Database

### Endpoint
```
POST /api/earthquakes/sync?page=1&per_page=100
```

### What It Does
1. ✅ Fetches earthquake data from `https://api.smrm.uz/api/earthquakes`
2. ✅ Checks for duplicates in database by:
   - `earthquake_id` (if integer)
   - `date` + `time` + `latitude` + `longitude`
3. ✅ Inserts only new records
4. ✅ Returns statistics

### Example Request
```bash
curl -X POST "http://localhost:8005/api/earthquakes/sync?page=1&per_page=100"
```

### Example Response
```json
{
  "detail": "Successfully synced 26 earthquakes, skipped 74 duplicates",
  "total_synced": 26,
  "total_skipped": 74,
  "total_processed": 100
}
```

### Duplicate Check Logic (Database)
```python
# Check 1: By earthquake_id
if integer_id:
    existing = db.query(Earthquake).filter(
        Earthquake.earthquake_id == integer_id
    ).first()
    if existing:
        skip  # Duplicate found

# Check 2: By date, time, location
existing_by_location = db.query(Earthquake).filter(
    Earthquake.date == date_val,
    Earthquake.time == time_val,
    Earthquake.latitude == lat_val,
    Earthquake.longitude == lon_val
).first()
if existing_by_location:
    skip  # Duplicate found
```

### Status
✅ **Working** - Manual trigger required

---

## Step 2: Database → ArcGIS

### Scheduler
- **Runs:** Every 10 minutes automatically
- **Starts:** 30 seconds after application startup
- **Target:** `https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer/2`

### What It Does
1. ✅ Reads ALL earthquakes from database
2. ✅ Gets existing features from ArcGIS (if token available)
3. ✅ Checks for duplicates in ArcGIS by:
   - `earthquake_id` (if exists in both)
   - `date` + `time` + `latitude` + `longitude`
4. ✅ Sends only new features in batches of 100
5. ✅ Logs detailed statistics

### Duplicate Check Logic (ArcGIS)
```python
def is_duplicate(earthquake, existing_features):
    for feature in existing_features:
        attrs = feature.get("attributes", {})
        
        # Check by earthquake_id
        if earthquake.earthquake_id and attrs.get("earthquake_id") == earthquake.earthquake_id:
            return True  # Duplicate
        
        # Check by date, time, location
        if (attrs.get("date") == earthquake.date and
            attrs.get("time") == earthquake.time and
            attrs.get("latitude") == float(earthquake.latitude) and
            attrs.get("longitude") == float(earthquake.longitude)):
            return True  # Duplicate
    
    return False  # Not duplicate, send to ArcGIS
```

### Expected Logs
```
[Starting ArcGIS sync from database...]
🔑 Attempting ArcGIS Server token authentication...
✅ Token obtained from: https://gis.uzspace.uz/arcgis/tokens/generateToken
📊 Found 62 total earthquakes in database
📊 Querying existing features from ArcGIS...
📊 Found 0 existing features in ArcGIS
📤 Preparing to send 62 new features (skipped 0 duplicates)
📤 Sending 62 features to ArcGIS...
✅ Successfully sent 62/62 features to ArcGIS
✅ ArcGIS sync completed in 3.45s: 62 sent, 0 skipped, 0 batches failed
⏰ Next ArcGIS sync in 10 minutes...
```

### Status
⚠️ **Configured but blocked by authentication**

---

## Complete Workflow Example

### Scenario: New earthquake occurs

**Time: 10:00 AM**
1. External API receives new earthquake data
2. Data available at `https://api.smrm.uz/api/earthquakes`

**Time: 10:05 AM** (Manual sync)
```bash
curl -X POST "http://localhost:8005/api/earthquakes/sync"
```
Response:
```json
{
  "total_synced": 1,
  "total_skipped": 0,
  "total_processed": 1
}
```
✅ New earthquake saved to database

**Time: 10:10 AM** (Auto-sync runs)
```
📊 Found 63 total earthquakes in database (62 old + 1 new)
📊 Found 62 existing features in ArcGIS
📤 Preparing to send 1 new feature (skipped 62 duplicates)
✅ Successfully sent 1/1 features to ArcGIS
```
✅ New earthquake sent to ArcGIS

**Result:**
- ✅ No duplicates in database
- ✅ No duplicates in ArcGIS
- ✅ All systems synchronized

---

## Monitoring

### Check Database Sync
```bash
# Trigger manual sync
curl -X POST "http://localhost:8005/api/earthquakes/sync"

# Check database count
curl "http://localhost:8005/api/earthquakes/?page=0&per_page=10"
```

### Check ArcGIS Sync
```bash
# Check sync status
curl "http://localhost:8005/arcgis-sync-status"

# View logs
docker-compose logs -f api | grep "ArcGIS"

# Check health
curl "http://localhost:8005/health"
```

### Status Endpoints

**`GET /health`**
```json
{
  "status": "healthy",
  "internal_sync": {
    "enabled": false,
    "note": "Use manual sync endpoint"
  },
  "arcgis_sync": {
    "enabled": true,
    "interval": "10 minutes",
    "is_syncing": false,
    "last_sync_time": "2025-12-11T15:30:00",
    "stats": {
      "total_sent": 62,
      "total_skipped": 0,
      "last_error": null
    }
  }
}
```

**`GET /arcgis-sync-status`**
```json
{
  "scheduler": {
    "enabled": true,
    "interval": "10 minutes",
    "target": "https://gis.uzspace.uz/.../FeatureServer/2"
  },
  "current_status": {
    "is_syncing": false,
    "last_sync_time": "2025-12-11T15:30:00"
  },
  "statistics": {
    "total_sent": 62,
    "total_skipped": 0,
    "last_error": null
  }
}
```

---

## Current Implementation Status

| Component | Status | Details |
|-----------|--------|---------|
| **External API Sync** | ✅ Working | Manual trigger via `/api/earthquakes/sync` |
| **Database Storage** | ✅ Working | PostgreSQL with duplicate checking |
| **Duplicate Check (DB)** | ✅ Working | By ID and location |
| **ArcGIS Scheduler** | ✅ Configured | Runs every 10 minutes |
| **Duplicate Check (ArcGIS)** | ✅ Implemented | By ID and location |
| **Layer Configuration** | ✅ Updated | Layer 2 (not 0) |
| **Token Generation** | ⚠️ **Needs Fix** | Credentials invalid |
| **Data Send to ArcGIS** | ❌ Blocked | Waiting for valid token |

---

## What's Needed to Complete

### Fix Authentication

**Current credentials don't work:**
```
Username: zilzila
Password: zilzila@6739space
```

**Get correct credentials from ArcGIS admin:**
1. Valid username and password, OR
2. OAuth2 Client ID and Client Secret

**Update configuration:**
```python
# In app/arcgis_sync_scheduler.py
ARCGIS_USERNAME = "correct_username"
ARCGIS_PASSWORD = "correct_password"
```

**Restart:**
```bash
docker-compose restart api
```

---

## Testing the Complete Flow

### Test 1: Database Sync
```bash
# Sync from external API
curl -X POST "http://localhost:8005/api/earthquakes/sync"

# Verify in database
curl "http://localhost:8005/api/earthquakes/?page=0&per_page=5"
```

### Test 2: Check Duplicates
```bash
# Sync again (should skip duplicates)
curl -X POST "http://localhost:8005/api/earthquakes/sync"

# Should show: total_skipped = 100
```

### Test 3: ArcGIS Sync (Once auth is fixed)
```bash
# Wait for auto-sync or check logs
docker-compose logs -f api | grep "ArcGIS sync completed"

# Should show: X sent, Y skipped
```

### Test 4: End-to-End
```bash
# 1. Clear database (optional, for testing)
# 2. Sync from external API
curl -X POST "http://localhost:8005/api/earthquakes/sync"

# 3. Wait 30 seconds for ArcGIS sync
sleep 30

# 4. Check logs
docker-compose logs api | grep -E "(synced|sent|skipped)"

# Should show:
# - Database: X synced, 0 skipped
# - ArcGIS: X sent, 0 skipped
```

---

## Summary

✅ **Database Sync:** Working perfectly
- Fetches from external API
- Checks duplicates
- Saves to PostgreSQL

✅ **ArcGIS Sync:** Fully implemented
- Reads all data from database
- Checks duplicates in ArcGIS
- Sends only new records
- Runs every 10 minutes

❌ **Blocker:** Authentication
- Need valid ArcGIS credentials
- Once fixed, entire flow will work automatically

**Once authentication is resolved, the complete flow will work seamlessly!** 🎯
