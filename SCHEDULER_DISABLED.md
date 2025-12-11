# Auto-Sync Scheduler - DISABLED

## Status

✅ **Auto-sync scheduler is now DISABLED**

The automatic 10-minute sync has been commented out. You must now sync manually.

## Manual Sync

### Endpoint
```
POST /api/earthquakes/sync?page=1&per_page=100
```

### Example
```bash
curl -X POST "http://localhost:8005/api/earthquakes/sync?page=1&per_page=100"
```

### Response
```json
{
  "detail": "Successfully synced 26 earthquakes, skipped 74 duplicates",
  "total_synced": 26,
  "total_skipped": 74,
  "total_processed": 100
}
```

## Duplicate Prevention

✅ **Still Active** - Two-level duplicate detection:

1. **By earthquake_id** - For records with integer IDs
2. **By date + time + location** - For all records

This ensures no duplicates even with manual syncs.

## Check Status

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "auto_sync": {
    "enabled": false,
    "interval": "DISABLED",
    "note": "Use manual sync endpoint"
  }
}
```

### Sync Status
```
GET /sync-status
```

**Response:**
```json
{
  "scheduler": {
    "enabled": false,
    "status": "DISABLED"
  },
  "manual_sync": {
    "endpoint": "POST /api/earthquakes/sync",
    "duplicate_prevention": "enabled"
  }
}
```

## Re-enable Auto-Sync

If you want to re-enable automatic sync, uncomment the code in:

### `/app/scheduler.py`
```python
# Uncomment these functions:
# - async def sync_earthquakes_task()
# - async def run_scheduler()
# - asyncio.create_task(run_scheduler()) in start_scheduler()
```

### `/app/main.py`
```python
# Update startup message and endpoints to show enabled=true
```

Then restart:
```bash
docker-compose restart api
```

## Current Configuration

- ✅ Manual sync only
- ✅ Duplicate prevention active
- ✅ Two-level duplicate detection
- ✅ Individual record error handling
- ✅ Proper resource management

## Benefits of Manual Sync

1. **Full Control** - Sync when you want
2. **No Background Load** - Server resources free
3. **Predictable** - No surprise syncs
4. **Same Protection** - Duplicate prevention still works
5. **Same Quality** - All error handling intact
