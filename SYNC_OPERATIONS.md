# Sync Operations Overview

## Two Different Sync Operations

### 1. External API → Database Sync (Manual)

**Endpoint:** `POST /api/earthquakes/sync`

**Purpose:** Fetch earthquake data FROM external API and save TO your database

**Flow:**
```
External API (api.smrm.uz) → Your Database (PostgreSQL)
```

**Usage:**
```bash
curl -X POST "http://localhost:8005/api/earthquakes/sync?page=1&per_page=100"
```

**Response:**
```json
{
  "detail": "Successfully synced 26 earthquakes, skipped 74 duplicates",
  "total_synced": 26,
  "total_skipped": 74,
  "total_processed": 100
}
```

**Features:**
- ✅ Manual trigger only
- ✅ Fetches from external API
- ✅ Saves to your database
- ✅ Checks for duplicates in database
- ✅ Pagination support

---

### 2. Database → ArcGIS Sync (Automatic)

**Scheduler:** Runs every 10 minutes automatically

**Purpose:** Send ALL earthquake data FROM your database TO ArcGIS Feature Server

**Flow:**
```
Your Database (PostgreSQL) → ArcGIS Feature Server (gis.uzspace.uz)
```

**Features:**
- ✅ Automatic (every 10 minutes)
- ✅ Reads ALL data from database
- ✅ Sends to ArcGIS Feature Server
- ✅ Checks for duplicates in ArcGIS
- ✅ Batch processing (100 features per batch)

**Monitoring:**
```bash
# Check status
curl http://localhost:8005/arcgis-sync-status

# View logs
docker-compose logs -f api | grep "ArcGIS"
```

**Expected Logs:**
```
[Starting ArcGIS sync from database...]
📊 Found 1500 total earthquakes in database
📊 Found 1200 existing features in ArcGIS
📤 Preparing to send 300 new features (skipped 1200 duplicates)
✅ Sent batch 1/3 (100 features)
✅ Sent batch 2/3 (100 features)
✅ Sent batch 3/3 (100 features)
✅ ArcGIS sync completed in 8.45s: 300 sent, 1200 skipped, 0 batches failed
⏰ Next ArcGIS sync in 10 minutes...
```

---

## Complete Data Flow

```
┌─────────────────┐
│  External API   │
│  (api.smrm.uz)  │
└────────┬────────┘
         │
         │ Manual Sync
         │ POST /api/earthquakes/sync
         ▼
┌─────────────────┐
│  Your Database  │
│  (PostgreSQL)   │
└────────┬────────┘
         │
         │ Auto Sync (Every 10 min)
         │ Background Scheduler
         ▼
┌─────────────────┐
│  ArcGIS Server  │
│ (gis.uzspace.uz)│
└─────────────────┘
```

## Duplicate Prevention

### Database Sync (External API → Database)
Checks duplicates by:
1. `earthquake_id` (if integer)
2. `date` + `time` + `latitude` + `longitude`

### ArcGIS Sync (Database → ArcGIS)
Checks duplicates by:
1. `earthquake_id` (if exists in both)
2. `date` + `time` + `latitude` + `longitude`

## Current Status

### External API Sync
- ✅ Working
- ⚙️ Manual trigger required
- 📍 Endpoint: `/api/earthquakes/sync`

### ArcGIS Sync
- ✅ Scheduler running
- ⏰ Every 10 minutes
- ❌ Authentication issue (needs fixing)
- 📊 Reads ALL database records
- 🔄 Sends only new records to ArcGIS

## Authentication Issue

**Current Problem:**
ArcGIS authentication is failing. The scheduler is running but cannot send data until authentication is resolved.

**What's Working:**
- ✅ Scheduler runs every 10 minutes
- ✅ Reads all data from database
- ✅ Duplicate checking logic
- ✅ Batch processing

**What's Not Working:**
- ❌ Token generation (HTTP 500 error)
- ❌ Cannot send data to ArcGIS

**To Fix:**
1. Verify credentials with ArcGIS admin
2. Get correct authentication URL
3. Update credentials in `arcgis_sync_scheduler.py`

## Monitoring

### Check Database Sync
```bash
# Trigger manual sync
curl -X POST "http://localhost:8005/api/earthquakes/sync"

# Check database records
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

## Summary

| Feature | External API Sync | ArcGIS Sync |
|---------|------------------|-------------|
| **Trigger** | Manual | Automatic (10 min) |
| **Source** | External API | Your Database |
| **Destination** | Your Database | ArcGIS Server |
| **Data Volume** | 100 records/page | ALL records |
| **Duplicate Check** | In Database | In ArcGIS |
| **Status** | ✅ Working | ⚠️ Auth Issue |
| **Endpoint** | POST /sync | Background Task |
