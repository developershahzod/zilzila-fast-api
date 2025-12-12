# New ArcGIS API Endpoints

## Overview

Two new API endpoints have been added to manage ArcGIS token generation and sync operations.

## Endpoints

### 1. Check ArcGIS Token

**Endpoint**: `GET /arcgis-token-check`

**Purpose**: Test if ArcGIS token can be generated with current credentials

**Method**: GET

**Authentication**: None required

#### Request

```bash
curl http://localhost:8005/arcgis-token-check
```

#### Response (Success)

```json
{
  "status": "success",
  "message": "Token generated successfully",
  "token_info": {
    "length": 150,
    "preview": "ENZv8H3YrJnY9XsyFSM5iPi1KE7zID...",
    "endpoint": "https://gis.uzspace.uz/uzspace/sharing/rest/generateToken",
    "client_type": "referer",
    "expiration": "20160 minutes (14 days)"
  },
  "timestamp": "2025-12-12T15:56:00.123456"
}
```

#### Response (Error)

```json
{
  "status": "error",
  "message": "Failed to generate token",
  "details": "Check application logs for detailed error information",
  "timestamp": "2025-12-12T15:56:00.123456"
}
```

#### Use Cases

- ✅ Verify credentials are correct
- ✅ Test token endpoint connectivity
- ✅ Troubleshoot authentication issues
- ✅ Check token expiration settings

---

### 2. Start ArcGIS Sync

**Endpoint**: `POST /arcgis-sync-start`

**Purpose**: Manually trigger ArcGIS sync from database to ArcGIS Feature Server

**Method**: POST

**Authentication**: None required

#### Request

```bash
curl -X POST http://localhost:8005/arcgis-sync-start
```

#### Response (Success)

```json
{
  "status": "success",
  "message": "ArcGIS sync completed",
  "statistics": {
    "total_sent": 14200,
    "total_skipped": 100,
    "last_error": null
  },
  "last_sync_time": "2025-12-12T15:56:30.123456",
  "features": {
    "retry_enabled": true,
    "max_retries": 3,
    "batch_size": 100
  }
}
```

#### Response (Already Running)

```json
{
  "status": "error",
  "message": "ArcGIS sync is already in progress",
  "is_syncing": true,
  "last_sync_time": "2025-12-12T15:50:00.123456"
}
```

#### Response (Error)

```json
{
  "status": "error",
  "message": "ArcGIS sync failed: Connection timeout"
}
```

#### Features

- ✅ Automatic token generation
- ✅ Duplicate prevention (checks existing features)
- ✅ Batch processing (100 features per batch)
- ✅ Automatic retry (3 retries per batch)
- ✅ Exponential backoff (2s, 4s, 8s)
- ✅ Detailed statistics

#### Use Cases

- ✅ Manually trigger sync after data updates
- ✅ Retry failed syncs with new token
- ✅ Test sync functionality
- ✅ Force immediate sync without waiting for scheduler

---

## Quick Start

### 1. Check Token

```bash
# Test if token generation works
curl http://localhost:8005/arcgis-token-check
```

### 2. Start Sync

```bash
# Manually start sync
curl -X POST http://localhost:8005/arcgis-sync-start
```

### 3. Check Status

```bash
# Check sync status
curl http://localhost:8005/arcgis-sync-status
```

---

## Testing Script

Use the provided test script:

```bash
./test_new_apis.sh
```

This will:
1. Check if server is running
2. Test token generation
3. Check sync status before
4. Optionally start manual sync
5. Check sync status after

---

## Integration Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8005"

# Check token
response = requests.get(f"{BASE_URL}/arcgis-token-check")
token_info = response.json()
print(f"Token status: {token_info['status']}")

# Start sync
response = requests.post(f"{BASE_URL}/arcgis-sync-start")
sync_result = response.json()
print(f"Sync status: {sync_result['status']}")
print(f"Features sent: {sync_result['statistics']['total_sent']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8005";

// Check token
fetch(`${BASE_URL}/arcgis-token-check`)
  .then(res => res.json())
  .then(data => console.log("Token status:", data.status));

// Start sync
fetch(`${BASE_URL}/arcgis-sync-start`, { method: "POST" })
  .then(res => res.json())
  .then(data => {
    console.log("Sync status:", data.status);
    console.log("Features sent:", data.statistics.total_sent);
  });
```

### cURL

```bash
# Check token
curl http://localhost:8005/arcgis-token-check | jq .

# Start sync
curl -X POST http://localhost:8005/arcgis-sync-start | jq .

# Check status
curl http://localhost:8005/arcgis-sync-status | jq .
```

---

## API Response Fields

### Token Check Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `message` | string | Human-readable message |
| `token_info.length` | integer | Token length in characters |
| `token_info.preview` | string | First 30 characters of token |
| `token_info.endpoint` | string | Token generation endpoint URL |
| `token_info.client_type` | string | Client type used (referer) |
| `token_info.expiration` | string | Token expiration time |
| `timestamp` | string | ISO 8601 timestamp |

### Sync Start Response

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `message` | string | Human-readable message |
| `statistics.total_sent` | integer | Number of features sent |
| `statistics.total_skipped` | integer | Number of duplicates skipped |
| `statistics.last_error` | string/null | Last error message or null |
| `last_sync_time` | string | ISO 8601 timestamp of sync |
| `features.retry_enabled` | boolean | Whether retry is enabled |
| `features.max_retries` | integer | Maximum retry attempts |
| `features.batch_size` | integer | Features per batch |

---

## Error Handling

### Token Generation Errors

**Error 401**: Invalid credentials
```json
{
  "status": "error",
  "message": "Failed to generate token",
  "details": "Check application logs for detailed error information"
}
```

**Solution**: Verify credentials in `app/arcgis_sync_scheduler.py`

### Sync Errors

**Sync Already Running**:
```json
{
  "status": "error",
  "message": "ArcGIS sync is already in progress",
  "is_syncing": true
}
```

**Solution**: Wait for current sync to complete

**Connection Error**:
```json
{
  "status": "error",
  "message": "ArcGIS sync failed: Connection timeout"
}
```

**Solution**: Check network connectivity and ArcGIS server status

---

## Monitoring

### Check Logs

Monitor sync progress in application logs:

```bash
tail -f app.log | grep -E "(Token|Sync|Batch)"
```

### Expected Log Output

```
🔑 Testing ArcGIS token generation...
✅ Token obtained from: https://gis.uzspace.uz/uzspace/sharing/rest/generateToken
🚀 Starting ArcGIS sync via API...
📦 Processing batch 1/143 (100 features)
✅ Batch 1/143 completed: 100 features sent
📦 Processing batch 2/143 (100 features)
✅ Batch 2/143 completed: 100 features sent
...
✅ ArcGIS sync completed in 145.23s: 14200 sent, 100 skipped, 0 batches failed
```

---

## Comparison with Legacy Endpoint

### Legacy: `/arcgis-sync-manual`

- Still works (redirects to new endpoint)
- Kept for backward compatibility
- Use new endpoint for new integrations

### New: `/arcgis-sync-start`

- ✅ Better naming
- ✅ More detailed response
- ✅ Includes retry information
- ✅ Recommended for new code

---

## API Documentation

Full interactive API documentation available at:

- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

---

## Summary

### New Endpoints

1. **`GET /arcgis-token-check`** - Test token generation
2. **`POST /arcgis-sync-start`** - Start manual sync

### Features

- ✅ Token validation without exposing full token
- ✅ Manual sync trigger with retry logic
- ✅ Detailed statistics and error reporting
- ✅ Backward compatible with legacy endpoint
- ✅ Easy integration with any HTTP client

### Testing

```bash
# Quick test
./test_new_apis.sh

# Or manually
curl http://localhost:8005/arcgis-token-check
curl -X POST http://localhost:8005/arcgis-sync-start
```

### Next Steps

1. Restart your application
2. Test token generation: `curl http://localhost:8005/arcgis-token-check`
3. Start sync: `curl -X POST http://localhost:8005/arcgis-sync-start`
4. Monitor results: `curl http://localhost:8005/arcgis-sync-status`
