# 🚀 ArcGIS API - Quick Reference

## New API Endpoints

### 1️⃣ Check Token
```bash
GET /arcgis-token-check
```
**Purpose**: Test if ArcGIS token can be generated

**Example**:
```bash
curl http://localhost:8005/arcgis-token-check
```

**Response**:
```json
{
  "status": "success",
  "token_info": {
    "length": 150,
    "preview": "ENZv8H3YrJnY9XsyFSM5iPi1KE7zID...",
    "expiration": "20160 minutes (14 days)"
  }
}
```

---

### 2️⃣ Start Sync
```bash
POST /arcgis-sync-start
```
**Purpose**: Manually start ArcGIS sync

**Example**:
```bash
curl -X POST http://localhost:8005/arcgis-sync-start
```

**Response**:
```json
{
  "status": "success",
  "statistics": {
    "total_sent": 14200,
    "total_skipped": 100,
    "last_error": null
  }
}
```

---

### 3️⃣ Check Status
```bash
GET /arcgis-sync-status
```
**Purpose**: Check current sync status

**Example**:
```bash
curl http://localhost:8005/arcgis-sync-status
```

---

## Quick Commands

### Test Everything
```bash
./test_new_apis.sh
```

### Check Token Only
```bash
curl http://localhost:8005/arcgis-token-check | jq .status
```

### Start Sync Only
```bash
curl -X POST http://localhost:8005/arcgis-sync-start | jq .status
```

### Check If Syncing
```bash
curl http://localhost:8005/arcgis-sync-status | jq .current_status.is_syncing
```

---

## Common Workflows

### 1. Before Starting Sync
```bash
# 1. Check token works
curl http://localhost:8005/arcgis-token-check

# 2. Check if already syncing
curl http://localhost:8005/arcgis-sync-status

# 3. Start sync
curl -X POST http://localhost:8005/arcgis-sync-start
```

### 2. Troubleshooting
```bash
# Check token generation
curl http://localhost:8005/arcgis-token-check

# Check last error
curl http://localhost:8005/arcgis-sync-status | jq .statistics.last_error

# View logs
tail -f app.log | grep -E "(Token|Error|Batch)"
```

### 3. Monitoring Sync
```bash
# Check if running
curl http://localhost:8005/arcgis-sync-status | jq .current_status.is_syncing

# Check progress (in logs)
tail -f app.log | grep "Batch"

# Check final results
curl http://localhost:8005/arcgis-sync-status | jq .statistics
```

---

## Response Status Codes

| Status | Meaning |
|--------|---------|
| `"success"` | Operation completed successfully |
| `"error"` | Operation failed |

---

## Features

✅ **Automatic token generation**  
✅ **Duplicate prevention**  
✅ **Batch processing** (100 features/batch)  
✅ **Auto-retry** (3 retries with exponential backoff)  
✅ **Detailed statistics**  
✅ **Real-time status**  

---

## Documentation

- **Interactive API Docs**: http://localhost:8005/docs
- **Full Documentation**: `NEW_ARCGIS_APIS.md`
- **Retry Mechanism**: `ARCGIS_RETRY_MECHANISM.md`

---

## Support

**Check logs**:
```bash
tail -f app.log
```

**Test script**:
```bash
./test_new_apis.sh
```

**API docs**:
```
http://localhost:8005/docs
```
