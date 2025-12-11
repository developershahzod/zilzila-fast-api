# ArcGIS Authentication Issue

## Problem

The ArcGIS Feature Server authentication is failing with HTTP 500 error.

## Test Results

Tested multiple authentication endpoints:
- ❌ `https://gis.uzspace.uz/portal/sharing/rest/generateToken` - 404 Not Found
- ❌ `https://gis.uzspace.uz/uzspacesrvr/sharing/rest/generateToken` - 500 Internal Server Error
- ❌ `https://gis.uzspace.uz/server/rest/generateToken` - 404 Not Found
- ❌ `https://gis.uzspace.uz/arcgis/sharing/rest/generateToken` - 404 Not Found

## Possible Causes

1. **Incorrect Credentials**
   - Username: `zilzila`
   - Password: `zilzila@6739space`
   - These credentials may be incorrect or expired

2. **Wrong Authentication Method**
   - Server might use OAuth2, SAML, or Windows Authentication
   - Token generation endpoint might be different

3. **Server Configuration**
   - Feature Server might not support token-based auth
   - Server might require different authentication flow

4. **Network/Firewall**
   - Authentication endpoint might be blocked
   - Requires VPN or internal network access

## Solutions

### Option 1: Verify Credentials with ArcGIS Admin

Contact the ArcGIS server administrator to:
1. Verify username and password
2. Confirm authentication method
3. Get correct token generation URL
4. Check if account has proper permissions

### Option 2: Use ArcGIS Portal Web Interface

1. Go to: `https://gis.uzspace.uz/portal`
2. Login with credentials
3. Navigate to Feature Server
4. Check authentication requirements

### Option 3: Check if Public Access is Enabled

Test if Feature Server allows anonymous access:

```bash
# Test query without token
curl "https://gis.uzspace.uz/uzspacesrvr/rest/services/Hosted/ZilzilaNuqtalari/FeatureServer/0/query?where=1=1&outFields=*&f=json"
```

### Option 4: Use Alternative Authentication

If server uses OAuth2 or other methods:
1. Get OAuth2 client ID and secret
2. Implement OAuth2 flow
3. Use refresh tokens

### Option 5: Manual Token Generation

If you can login to ArcGIS Portal:
1. Login to portal web interface
2. Generate token manually
3. Use long-lived token (not recommended for production)
4. Update scheduler to use fixed token

## Temporary Workaround

Until authentication is fixed, you can:

1. **Disable ArcGIS Sync**
   
   Edit `/app/main.py`:
   ```python
   @app.on_event("startup")
   async def startup_event():
       logger.info("Starting application...")
       start_scheduler()
       # start_arcgis_scheduler()  # Disabled until auth is fixed
       logger.info("Application started")
   ```

2. **Use Manual Export**
   
   Export data manually and upload to ArcGIS:
   ```bash
   # Get GeoJSON
   curl "http://localhost:8005/api/earthquakes/download/geojson" -o earthquakes.geojson
   
   # Upload to ArcGIS Portal manually
   ```

3. **Use Alternative Sync Method**
   
   If you have ArcGIS Pro or QGIS:
   - Connect to PostgreSQL database directly
   - Export to shapefile
   - Upload to Feature Server

## Next Steps

1. **Contact ArcGIS Administrator**
   - Request correct authentication details
   - Verify Feature Server URL
   - Check permissions

2. **Test Authentication Manually**
   - Try logging in to web portal
   - Generate token from portal
   - Test token with Feature Server

3. **Update Configuration**
   - Once correct auth method is known
   - Update `arcgis_sync_scheduler.py`
   - Test with new credentials

## Current Status

- ✅ Scheduler code is working
- ✅ Duplicate prevention implemented
- ✅ Error handling in place
- ❌ Authentication failing
- ⏸️  Sync paused until auth is resolved

## Contact

For ArcGIS server access issues, contact:
- ArcGIS Server Administrator
- IT Department
- GIS Team Lead
