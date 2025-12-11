# Sync Optimization & Resource Management

## Overview

The auto-sync system is optimized to prevent server overload and duplicate synchronization.

## Protection Mechanisms

### 1. **Lock-Based Duplicate Prevention**

```python
# Global asyncio lock
_sync_lock = asyncio.Lock()
_is_syncing = False
```

**How it works:**
- Only ONE sync can run at a time
- If sync is already running, new requests are skipped
- Lock is automatically released when sync completes

**Benefits:**
✅ No concurrent syncs  
✅ No database connection overload  
✅ No duplicate data processing  

### 2. **Status Checking**

```python
if _is_syncing:
    logger.warning("⚠️ Sync already in progress, skipping this run")
    return
```

**Protection:**
- Checks if sync is running before starting
- Skips execution if already in progress
- Logs warning for monitoring

### 3. **Resource Management**

**Database Connections:**
```python
db: Session = None
try:
    db = SessionLocal()
    # ... sync logic ...
finally:
    if db:
        db.close()  # Always close connection
```

**Benefits:**
✅ Connections always closed  
✅ No connection leaks  
✅ Efficient resource usage  

### 4. **Individual Record Processing**

```python
# Insert records one by one
for earthquake in earthquakes:
    try:
        db.add(earthquake)
        db.flush()
    except Exception as e:
        db.rollback()
        skipped += 1
```

**Benefits:**
✅ Bad records don't block good ones  
✅ Partial success possible  
✅ Minimal database load  

### 5. **Startup Delay**

```python
# Run first sync after 30 seconds
await asyncio.sleep(30)
```

**Purpose:**
- Gives application time to fully start
- Ensures database is ready
- Prevents startup conflicts

## Monitoring

### Check Sync Status

**Endpoint:** `GET /sync-status`

```json
{
  "scheduler": {
    "enabled": true,
    "interval_seconds": 600,
    "interval_minutes": 10
  },
  "current_sync": {
    "is_running": false,
    "last_completed": "2025-12-11T15:30:00"
  },
  "protection": {
    "duplicate_prevention": "enabled",
    "lock_based": true,
    "resource_management": "active"
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```json
{
  "status": "healthy",
  "auto_sync": {
    "enabled": true,
    "interval": "10 minutes",
    "is_syncing": false,
    "last_sync_time": "2025-12-11T15:30:00"
  }
}
```

## Performance Metrics

### Sync Duration
- Logged for each sync operation
- Example: `✅ Sync completed in 2.34s`

### Resource Usage
- **Database Connections:** 1 per sync (properly closed)
- **Memory:** Minimal (processes 100 records at a time)
- **CPU:** Low (async operations)

## Load Prevention

### 1. **Controlled Batch Size**
- Fetches only 100 records per sync
- Prevents memory overflow
- Reduces API load

### 2. **Duplicate Detection**
- Checks existing records before insert
- Skips duplicates automatically
- Reduces database writes

### 3. **Error Isolation**
- Individual record errors don't fail entire batch
- Failed records are skipped
- Sync continues with remaining records

### 4. **Time-Based Execution**
- Fixed 10-minute interval
- No overlap possible
- Predictable resource usage

## Logs

### Normal Operation
```
[2025-12-11 15:30:00] Starting automatic earthquake sync...
[2025-12-11 15:30:02] ✅ Sync completed in 2.34s: 80 synced, 20 skipped, 100 total processed
[2025-12-11 15:30:02] ⏰ Next sync in 10 minutes...
```

### Duplicate Prevention
```
[2025-12-11 15:30:00] Starting automatic earthquake sync...
[2025-12-11 15:30:00] ⚠️ Sync already in progress, skipping this run
```

### Error Handling
```
[2025-12-11 15:30:00] Starting automatic earthquake sync...
[2025-12-11 15:30:01] Failed to insert earthquake: invalid data
[2025-12-11 15:30:02] ✅ Sync completed in 2.45s: 79 synced, 21 skipped, 100 total processed
```

## Configuration

### Change Sync Interval

Edit `/app/scheduler.py`:

```python
# 5 minutes
await asyncio.sleep(300)

# 15 minutes
await asyncio.sleep(900)

# 30 minutes
await asyncio.sleep(1800)

# 1 hour
await asyncio.sleep(3600)
```

### Change Batch Size

Edit `/app/scheduler.py`:

```python
# Fetch 50 records
api_data = await ApiService.fetch_earthquakes(page=1, per_page=50)

# Fetch 200 records
api_data = await ApiService.fetch_earthquakes(page=1, per_page=200)
```

## Best Practices

1. **Monitor Logs** - Check for warnings and errors
2. **Check Status** - Use `/sync-status` endpoint regularly
3. **Adjust Interval** - Based on data update frequency
4. **Batch Size** - Balance between freshness and load
5. **Database Health** - Monitor connection pool usage

## Troubleshooting

### Sync Not Running
- Check logs: `docker-compose logs api | grep "scheduler"`
- Verify status: `GET /sync-status`
- Restart: `docker-compose restart api`

### High Resource Usage
- Reduce batch size (per_page)
- Increase sync interval
- Check for database connection leaks

### Duplicate Warnings
- Normal if manual sync triggered during auto-sync
- Lock prevents actual duplicates
- No action needed

## Summary

✅ **No Duplicate Syncs** - Lock-based prevention  
✅ **No Server Overload** - Controlled batch processing  
✅ **Resource Efficient** - Proper connection management  
✅ **Error Resilient** - Individual record handling  
✅ **Fully Monitored** - Status endpoints and logs  
