# How to Get ArcGIS OAuth2 Credentials

## Current Status

✅ **OAuth2 authentication implemented**  
❌ **Credentials not working**

## What You Need

To use OAuth2 authentication, you need:

1. **Client ID** (currently using: `zilzila`)
2. **Client Secret** (currently using: `zilzila@6739space`)

These are **NOT** the same as username/password!

## How to Get OAuth2 Credentials

### Option 1: ArcGIS Portal (Recommended)

1. **Login to ArcGIS Portal**
   - Go to: `https://gis.uzspace.uz/portal`
   - Login with admin account

2. **Navigate to Organization Settings**
   - Click on **Organization** → **Settings**
   - Go to **Security** tab

3. **Register New Application**
   - Click **New Application**
   - Choose **Application Type**: Server Application
   - Fill in details:
     - Name: "Earthquake Sync Service"
     - Redirect URI: `https://gis.uzspace.uz`
   - Click **Register**

4. **Get Credentials**
   - After registration, you'll see:
     - **Client ID**: `abc123xyz...`
     - **Client Secret**: `def456uvw...`
   - Copy these values

5. **Grant Permissions**
   - Make sure the application has permission to:
     - Add features to Feature Services
     - Access the ZilzilaNuqtalari Feature Service

### Option 2: Contact ArcGIS Administrator

Ask them to provide:

```
Client ID: [the actual client_id]
Client Secret: [the actual client_secret]
```

For the application that has access to:
- Feature Service: `ZilzilaNuqtalari`
- Permission: Add Features

### Option 3: Use Existing Application

If an OAuth2 application already exists:

1. Ask admin for the Client ID and Client Secret
2. Verify it has access to the Feature Service
3. Update the configuration

## Update Configuration

Once you have the credentials:

### Edit `/app/arcgis_sync_scheduler.py`

```python
# OAuth2 Configuration
ARCGIS_CLIENT_ID = "your_actual_client_id_here"
ARCGIS_CLIENT_SECRET = "your_actual_client_secret_here"
```

### Restart API

```bash
docker-compose restart api
```

### Monitor Logs

```bash
docker-compose logs -f api | grep "OAuth2"
```

**Expected output:**
```
✅ OAuth2 token obtained from: https://gis.uzspace.uz/...
✅ Token type: bearer
✅ Expires in: 3600 seconds
✅ Token (first 30 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

## Test OAuth2 Manually

You can test OAuth2 authentication manually:

```bash
curl -X POST "https://gis.uzspace.uz/portal/sharing/rest/oauth2/token" \
  -d "f=json" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=client_credentials"
```

**Success response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "bearer"
}
```

**Error response:**
```json
{
  "error": "invalid_client",
  "error_description": "Invalid client credentials"
}
```

## Alternative: Username/Password Token

If OAuth2 is not available, you can use username/password:

### Ask Admin For

```
Username: [actual_username]
Password: [actual_password]
Token URL: [correct_generateToken_endpoint]
```

### Update Configuration

```python
ARCGIS_USERNAME = "actual_username"
ARCGIS_PASSWORD = "actual_password"
```

## Common Issues

### Issue 1: "invalid_client"
**Cause:** Client ID or Client Secret is wrong  
**Solution:** Verify credentials with admin

### Issue 2: "unauthorized_client"
**Cause:** Application doesn't have required permissions  
**Solution:** Grant Feature Service access to the application

### Issue 3: "Token Required" (499)
**Cause:** Token generation failed, but Feature Service requires auth  
**Solution:** Fix token generation first

### Issue 4: 404 Not Found
**Cause:** Wrong OAuth2 endpoint URL  
**Solution:** Verify correct URL with admin

## URLs Being Tried

The system tries these OAuth2 URLs:

1. `https://gis.uzspace.uz/portal/sharing/rest/oauth2/token`
2. `https://gis.uzspace.uz/uzspacesrvr/sharing/rest/oauth2/token`
3. `https://gis.uzspace.uz/sharing/rest/oauth2/token`

If none work, ask admin for the correct URL.

## Summary

**Current Situation:**
- ✅ OAuth2 code implemented
- ✅ Tries 3 different OAuth2 URLs
- ✅ Falls back to traditional auth
- ❌ No valid credentials

**What You Need:**
1. Contact ArcGIS administrator
2. Get OAuth2 Client ID and Client Secret
3. Update configuration
4. Restart API
5. Data will sync automatically

**Once credentials are correct, everything will work immediately!** 🔐
