# ArcGIS Sync - Token Required Issue

## Problem Identified

The ArcGIS Feature Server **requires authentication** and is rejecting all requests without a valid token.

## Error Details

```json
{
  "code": 499,
  "message": "Token Required",
  "details": []
}
```

## What's Working

✅ **Scheduler:** Running every 10 minutes  
✅ **Database Query:** Reading all 62 earthquakes  
✅ **Feature Conversion:** Converting to ArcGIS format correctly  
✅ **Duplicate Check:** Working (0 duplicates found)  
✅ **Network Connection:** Can reach ArcGIS server  
✅ **Request Format:** Correct URL and data format  

## What's NOT Working

❌ **Authentication:** Cannot obtain valid token  
❌ **Token Generation:** All endpoints return errors:
- `/portal/sharing/rest/generateToken` → 404 Not Found
- `/uzspacesrvr/sharing/rest/generateToken` → 500 Internal Server Error

## Current Credentials

```
Username: zilzila
Password: zilzila@6739space
Server: https://gis.uzspace.uz
```

**These credentials are NOT working.**

## Sample Feature Being Sent

The data format is correct:

```json
{
  "geometry": {
    "x": 71.8087,
    "y": 41.60903,
    "spatialReference": {
      "wkid": 4326
    }
  },
  "attributes": {
    "earthquake_id": 6916,
    "date": "12.06.2025",
    "time": "05:44:15",
    "latitude": 41.60903,
    "longitude": 71.8087,
    "depth": 7.0,
    "magnitude": 2.4,
    "magnitude_type": "Mb",
    "epicenter": "Qirg'iziston",
    "epicenter_ru": "Кыргызстане",
    "color": "#30b532",
    "description": "...",
    "is_perceptabily": false
  }
}
```

## Required Actions

### 1. Contact ArcGIS Administrator

**Ask for:**
- ✅ Correct username and password
- ✅ Correct token generation URL
- ✅ Authentication method (Token, OAuth2, Windows Auth, etc.)
- ✅ Feature Service permissions
- ✅ Any IP restrictions or firewall rules

### 2. Test Credentials Manually

**Option A: Web Portal**
1. Go to: `https://gis.uzspace.uz/portal`
2. Try to login with credentials
3. If successful, navigate to Feature Service
4. Try to generate token manually

**Option B: REST API**
1. Open browser
2. Go to: `https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer`
3. Check if it requires authentication
4. Try to access with credentials

### 3. Alternative Solutions

**If credentials cannot be obtained:**

**Option A: Manual Upload**
```bash
# Export from database
curl "http://localhost:8005/api/earthquakes/download/geojson" -o earthquakes.geojson

# Upload manually to ArcGIS Portal
# Use web interface or ArcGIS Pro
```

**Option B: Direct Database Connection**
```
Use ArcGIS Pro or QGIS to:
1. Connect directly to PostgreSQL database
2. Query earthquake data
3. Publish to Feature Service
```

**Option C: Different Authentication Method**
If server uses OAuth2 or SAML:
1. Get OAuth2 credentials
2. Implement OAuth2 flow
3. Update scheduler code

## Temporary Workaround

### Disable ArcGIS Sync

Edit `/app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    start_scheduler()
    # start_arcgis_scheduler()  # DISABLED - Token Required
    logger.info("Application started")
```

Then restart:
```bash
docker-compose restart api
```

## Once Credentials Are Obtained

### Update Configuration

Edit `/app/arcgis_sync_scheduler.py`:

```python
# Update these lines
ARCGIS_USERNAME = "correct_username"
ARCGIS_PASSWORD = "correct_password"
```

### Test Authentication

Run test script:
```bash
docker-compose exec api python test_arcgis_auth.py
```

Should see:
```
✅ SUCCESS! Token obtained
Token (first 50 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Restart and Monitor

```bash
docker-compose restart api
docker-compose logs -f api | grep "ArcGIS"
```

Expected logs:
```
✅ ArcGIS token obtained successfully
📊 Found 62 earthquakes in database
📤 Preparing to send 62 new features
✅ Sent batch 1/1 (62 features)
✅ ArcGIS sync completed: 62 sent, 0 skipped
```

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Scheduler | ✅ Working | Runs every 10 minutes |
| Database Query | ✅ Working | Reads all 62 records |
| Data Format | ✅ Correct | GeoJSON format valid |
| Network | ✅ Working | Can reach server |
| Authentication | ❌ **FAILING** | **Token Required** |
| Data Sync | ❌ Blocked | Cannot proceed without token |

## Next Step

**URGENT: Contact ArcGIS administrator to get valid credentials.**

Without valid authentication, the sync cannot proceed. Everything else is working correctly.

## Contact Information

For ArcGIS access, contact:
- **GIS Administrator**
- **IT Department**  
- **System Administrator**

Provide them with:
- Server URL: `https://gis.uzspace.uz`
- Feature Service: `ZilzilaNuqtalari`
- Purpose: Automated earthquake data sync
- Required permissions: Add features to Feature Service
