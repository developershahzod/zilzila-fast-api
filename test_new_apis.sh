#!/bin/bash
# Test the new ArcGIS API endpoints

BASE_URL="http://localhost:8005"

echo "============================================================"
echo "Testing New ArcGIS API Endpoints"
echo "============================================================"
echo ""

# Check if server is running
echo "1. Checking if server is running..."
if ! curl -s ${BASE_URL}/health > /dev/null 2>&1; then
    echo "❌ ERROR: Server is not running on port 8005"
    echo ""
    echo "Please start the server first:"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8005"
    echo ""
    exit 1
fi
echo "✅ Server is running"
echo ""

# Test 1: Check ArcGIS Token
echo "============================================================"
echo "TEST 1: Check ArcGIS Token Generation"
echo "============================================================"
echo "Endpoint: GET /arcgis-token-check"
echo ""

response=$(curl -s ${BASE_URL}/arcgis-token-check)
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

echo ""
echo ""

# Test 2: Check Sync Status (Before)
echo "============================================================"
echo "TEST 2: Check ArcGIS Sync Status (Before Sync)"
echo "============================================================"
echo "Endpoint: GET /arcgis-sync-status"
echo ""

response=$(curl -s ${BASE_URL}/arcgis-sync-status)
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

echo ""
echo ""

# Test 3: Start Manual Sync
echo "============================================================"
echo "TEST 3: Start ArcGIS Sync Manually"
echo "============================================================"
echo "Endpoint: POST /arcgis-sync-start"
echo ""
echo "⚠️  This will take several minutes to complete..."
echo "Press Ctrl+C to cancel, or wait for completion"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting sync..."
    echo ""
    
    response=$(curl -s -X POST ${BASE_URL}/arcgis-sync-start)
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    echo ""
    echo ""
    
    # Test 4: Check Sync Status (After)
    echo "============================================================"
    echo "TEST 4: Check ArcGIS Sync Status (After Sync)"
    echo "============================================================"
    echo "Endpoint: GET /arcgis-sync-status"
    echo ""
    
    response=$(curl -s ${BASE_URL}/arcgis-sync-status)
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "Sync cancelled"
fi

echo ""
echo ""
echo "============================================================"
echo "Testing Complete"
echo "============================================================"
echo ""
echo "Available Endpoints:"
echo "  GET  /arcgis-token-check   - Test token generation"
echo "  POST /arcgis-sync-start    - Start manual sync"
echo "  GET  /arcgis-sync-status   - Check sync status"
echo ""
echo "Documentation: ${BASE_URL}/docs"
echo "============================================================"
