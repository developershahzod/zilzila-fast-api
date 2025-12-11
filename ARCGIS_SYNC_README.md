# ArcGIS Feature Server Auto-Sync

## Overview

Automatic synchronization of earthquake data to ArcGIS Feature Server every 10 minutes with duplicate prevention.

## Configuration

### ArcGIS Server
- **URL:** `https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer`
- **Username:** `zilzila`
- **Password:** `zilzila@6739space`

### Sync Settings
- **Interval:** 10 minutes (600 seconds)
- **Batch Size:** 100 features per request
- **Records Checked:** Last 1000 earthquakes from database

## Features

### ✅ Duplicate Prevention

**Two-Level Check:**

1. **By earthquake_id** - Matches integer IDs
2. **By date + time + location** - Matches coordinates and timestamp

**Result:** No duplicates sent to ArcGIS

### ✅ Automatic Authentication

- Gets token automatically before each sync
- Handles token expiration
- Logs authentication status

### ✅ Batch Processing

- Sends features in batches of 100
- Prevents server overload
- Handles large datasets efficiently

### ✅ Error Handling

- Continues on individual feature errors
- Logs all errors for debugging
- Tracks success/failure statistics

### ✅ Resource Management

- Lock-based concurrent prevention
- Proper database connection cleanup
- Async/await for non-blocking operation

## Data Format

### Earthquake to ArcGIS Feature

```json
{
  "geometry": {
    "x": 70.72,
    "y": 40.88,
    "spatialReference": {"wkid": 4326}
  },
  "attributes": {
    "earthquake_id": 6982,
    "date": "06.12.2025",
    "time": "19:18:00",
    "latitude": 40.88,
    "longitude": 70.72,
    "depth": 11,
    "magnitude": 3.4,
    "magnitude_type": "mb",
    "epicenter": "O'zbekiston",
    "epicenter_ru": "Ўзбекистон",
    "epicenter_en": null,
    "color": "#e48601",
    "description": "...",
    "is_perceptabily": false,
    "created_at": "2025-12-11T10:26:38",
    "updated_at": "2025-12-11T10:26:38"
  }
}
```

## Monitoring

### Check Sync Status

**Endpoint:** `GET /arcgis-sync-status`

```bash
curl http://localhost:8005/arcgis-sync-status
```

**Response:**
```json
{
  "scheduler": {
    "enabled": true,
    "interval": "10 minutes",
    "target": "https://gis.uzspace.uz/..."
  },
  "current_status": {
    "is_syncing": false,
    "last_sync_time": "2025-12-11T15:30:00"
  },
  "statistics": {
    "total_sent": 150,
    "total_skipped": 850,
    "last_error": null
  },
  "features": {
    "duplicate_prevention": "enabled",
    "check_by_id": true,
    "check_by_location": true,
    "batch_size": 100
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8005/health
```

**Response includes:**
```json
{
  "status": "healthy",
  "arcgis_sync": {
    "enabled": true,
    "interval": "10 minutes",
    "is_syncing": false,
    "last_sync_time": "2025-12-11T15:30:00",
    "stats": {
      "total_sent": 150,
      "total_skipped": 850,
      "last_error": null
    }
  }
}
```

### Combined Status

**Endpoint:** `GET /sync-status`

Shows both internal and ArcGIS sync status.

## Logs

### Normal Operation
```
[2025-12-11 15:30:00] Starting ArcGIS sync...
✅ ArcGIS token obtained successfully
📊 Found 1000 earthquakes in database
📊 Found 850 existing features in ArcGIS
📤 Preparing to send 150 new features (skipped 850 duplicates)
✅ Sent batch 1 (100 features)
✅ Sent batch 2 (50 features)
✅ ArcGIS sync completed in 5.23s: 150 sent, 850 skipped
⏰ Next ArcGIS sync in 10 minutes...
```

### Duplicate Prevention
```
📊 Found 1000 earthquakes in database
📊 Found 1000 existing features in ArcGIS
📤 Preparing to send 0 new features (skipped 1000 duplicates)
✅ ArcGIS sync completed in 2.15s: 0 sent, 1000 skipped
```

### Error Handling
```
❌ Error getting ArcGIS token: Connection timeout
❌ ArcGIS sync failed: Failed to obtain ArcGIS token
```

## View Logs

```bash
# Real-time logs
docker-compose logs -f api

# Search for ArcGIS sync
docker-compose logs api | grep "ArcGIS"

# Last 50 lines
docker-compose logs --tail=50 api
```

## Configuration Changes

### Change Sync Interval

Edit `/app/arcgis_sync_scheduler.py`:

```python
# 5 minutes
await asyncio.sleep(300)

# 15 minutes
await asyncio.sleep(900)

# 30 minutes
await asyncio.sleep(1800)
```

### Change Batch Size

Edit `/app/arcgis_sync_scheduler.py`:

```python
# Smaller batches (50)
batch_size = 50

# Larger batches (200)
batch_size = 200
```

### Change Records Limit

Edit `/app/arcgis_sync_scheduler.py`:

```python
# Check last 500 records
earthquakes = db.query(Earthquake).order_by(desc(Earthquake.id)).limit(500).all()

# Check last 2000 records
earthquakes = db.query(Earthquake).order_by(desc(Earthquake.id)).limit(2000).all()
```

### Update Credentials

Edit `/app/arcgis_sync_scheduler.py`:

```python
ARCGIS_USERNAME = "your_username"
ARCGIS_PASSWORD = "your_password"
```

## Troubleshooting

### Sync Not Running
1. Check logs: `docker-compose logs api | grep "ArcGIS"`
2. Verify startup: Look for "ArcGIS sync scheduler started"
3. Restart: `docker-compose restart api`

### Authentication Errors
- Verify credentials in `arcgis_sync_scheduler.py`
- Check ArcGIS server availability
- Verify token generation URL

### No Features Sent
- All features might be duplicates (normal)
- Check `total_skipped` in stats
- Verify database has new records

### Connection Errors
- Check network connectivity
- Verify ArcGIS server URL
- Check firewall settings

## Disable ArcGIS Sync

Edit `/app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    start_scheduler()
    # start_arcgis_scheduler()  # Comment this line
    logger.info("Application started")
```

Restart:
```bash
docker-compose restart api
```

## Performance

- **Sync Duration:** 2-10 seconds (depends on feature count)
- **Database Queries:** 2 per sync (earthquakes + existing check)
- **API Calls:** 2-3 per sync (token + query + add features)
- **Memory Usage:** Minimal (processes in batches)
- **CPU Usage:** Low (async operations)

## Security

- ✅ Credentials stored in code (consider environment variables)
- ✅ HTTPS connection to ArcGIS
- ✅ Token-based authentication
- ✅ No sensitive data in logs

## Summary

✅ **Automatic** - Runs every 10 minutes  
✅ **Duplicate Prevention** - Two-level checking  
✅ **Batch Processing** - Efficient data transfer  
✅ **Error Resilient** - Continues on failures  
✅ **Fully Monitored** - Status endpoints and logs  
✅ **Resource Efficient** - Lock-based, async operations  
