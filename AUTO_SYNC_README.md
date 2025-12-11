# Automatic Earthquake Data Synchronization

## Overview

The API now includes an **automatic background scheduler** that syncs earthquake data from the external API every 10 minutes.

## Features

✅ **Automatic Sync** - Runs every 10 minutes  
✅ **Background Task** - Doesn't block API requests  
✅ **Error Handling** - Continues running even if sync fails  
✅ **Logging** - Detailed logs of each sync operation  
✅ **Manual Sync** - Can still trigger manual sync via API  

## How It Works

1. **On Startup**: Scheduler starts automatically when the application starts
2. **Every 10 Minutes**: Fetches latest 100 earthquakes from external API
3. **Smart Sync**: 
   - Checks for duplicates (skips existing records)
   - Handles integer and string IDs
   - Inserts records one by one (skips problematic records)
4. **Logging**: Reports success/failure and statistics

## Endpoints

### Check Scheduler Status
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "auto_sync": {
    "enabled": true,
    "interval": "10 minutes",
    "endpoint": "/api/earthquakes/sync"
  }
}
```

### Manual Sync (Still Available)
```
POST /api/earthquakes/sync?page=1&per_page=100
```

**Response:**
```json
{
  "detail": "Successfully synced 80 earthquakes, skipped 20 duplicates",
  "total_synced": 80,
  "total_skipped": 20,
  "total_processed": 100
}
```

## Logs

The scheduler logs all activities:

```
[2025-12-11 15:30:00] 🚀 Earthquake sync scheduler started (runs every 10 minutes)
[2025-12-11 15:30:00] Starting automatic earthquake sync...
[2025-12-11 15:30:05] ✅ Sync completed: 80 synced, 20 skipped, 100 total processed
[2025-12-11 15:30:05] ⏰ Next sync in 10 minutes...
[2025-12-11 15:40:00] Starting automatic earthquake sync...
```

## Configuration

To change the sync interval, edit `/app/scheduler.py`:

```python
# Current: 10 minutes (600 seconds)
await asyncio.sleep(600)

# Change to 5 minutes:
await asyncio.sleep(300)

# Change to 1 hour:
await asyncio.sleep(3600)
```

## Monitoring

### View Logs in Docker
```bash
# Follow logs in real-time
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api

# Search for sync logs
docker-compose logs api | grep "Sync completed"
```

### Check Last Sync
Query the database to see the most recent earthquakes:
```
GET /api/earthquakes/?page=0&per_page=10&sort=datetime_desc
```

## Disabling Auto-Sync

To disable automatic sync, comment out the scheduler in `/app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    """
    Start background tasks on application startup
    """
    # logger.info("Starting background scheduler...")
    # start_scheduler()
    # logger.info("Background scheduler started - syncing every 10 minutes")
    pass
```

## Troubleshooting

### Scheduler Not Running
1. Check logs: `docker-compose logs api`
2. Verify startup event: Look for "Background scheduler started"
3. Restart container: `docker-compose restart api`

### Sync Failures
- Check external API availability
- Verify database connection
- Review error logs for specific issues

### High Memory Usage
- Reduce `per_page` in scheduler (default: 100)
- Increase sync interval (default: 10 minutes)

## Benefits

1. **Always Up-to-Date** - Latest earthquake data every 10 minutes
2. **No Manual Intervention** - Runs automatically
3. **Reliable** - Continues even if some records fail
4. **Efficient** - Skips duplicates automatically
5. **Transparent** - Detailed logging of all operations
