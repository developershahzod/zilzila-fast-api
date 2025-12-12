#!/bin/bash
# Trigger manual ArcGIS sync to retry with new token configuration

echo "============================================================"
echo "Triggering Manual ArcGIS Sync"
echo "============================================================"
echo ""
echo "This will:"
echo "  1. Reset previous error stats"
echo "  2. Generate new token with correct endpoint"
echo "  3. Sync all earthquakes to ArcGIS"
echo ""
echo "------------------------------------------------------------"
echo ""

# Check if server is running
if ! curl -s http://localhost:8005/health > /dev/null 2>&1; then
    echo "❌ ERROR: FastAPI server is not running on port 8005"
    echo ""
    echo "Please start the server first:"
    echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8005"
    echo ""
    exit 1
fi

echo "✅ Server is running"
echo ""
echo "Triggering manual sync..."
echo ""

# Trigger manual sync
response=$(curl -s -X POST http://localhost:8005/arcgis-sync-manual)

echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

echo ""
echo "------------------------------------------------------------"
echo ""
echo "Check detailed status:"
echo "  curl http://localhost:8005/arcgis-sync-status"
echo ""
echo "Or visit: http://localhost:8005/docs"
echo "============================================================"
