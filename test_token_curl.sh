#!/bin/bash
# Test ArcGIS token generation using curl

echo "============================================================"
echo "Testing ArcGIS Token Generation"
echo "============================================================"
echo ""
echo "Endpoint: https://gis.uzspace.uz/arcgis/sharing/rest/generateToken"
echo "Username: farhodmf"
echo ""

curl -k -X POST "https://gis.uzspace.uz/arcgis/sharing/rest/generateToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=farhodmf" \
  -d "password=AQ!SW@de3?" \
  -d "client=requestip" \
  -d "expiration=60" \
  -d "f=json" \
  --max-time 10 \
  -w "\n\nHTTP Status: %{http_code}\n"

echo ""
echo "============================================================"
