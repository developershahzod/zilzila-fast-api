#!/bin/bash
# Quick test for the token check API

echo "============================================================"
echo "Testing ArcGIS Token Check API"
echo "============================================================"
echo ""

BASE_URL="http://localhost:8005"

# Check if server is running
echo "Checking if server is running..."
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

echo "Testing: GET /arcgis-token-check"
echo "------------------------------------------------------------"
echo ""

curl -X 'GET' \
  "${BASE_URL}/arcgis-token-check" \
  -H 'accept: application/json' | python3 -m json.tool 2>/dev/null || curl -X 'GET' "${BASE_URL}/arcgis-token-check" -H 'accept: application/json'

echo ""
echo ""
echo "============================================================"
echo "Test Complete"
echo "============================================================"
