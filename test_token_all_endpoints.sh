#!/bin/bash
# Test multiple ArcGIS token generation endpoints

echo "============================================================"
echo "Testing Multiple ArcGIS Token Endpoints"
echo "============================================================"
echo ""

endpoints=(
  "https://gis.uzspace.uz/arcgis/sharing/rest/generateToken"
  "https://gis.uzspace.uz/portal/sharing/rest/generateToken"
  "https://gis.uzspace.uz/arcgis/tokens/generateToken"
  "https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken"
  "https://gis.uzspace.uz/server/tokens/generateToken"
  "https://gis.uzspace.uz/arcgis/admin/generateToken"
)

for endpoint in "${endpoints[@]}"; do
  echo ""
  echo "------------------------------------------------------------"
  echo "Testing: $endpoint"
  echo "------------------------------------------------------------"
  
  response=$(curl -k -s -X POST "$endpoint" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=farhodmf" \
    -d "password=AQ!SW@de3?" \
    -d "client=requestip" \
    -d "expiration=60" \
    -d "f=json" \
    --max-time 10 \
    -w "\nHTTP_STATUS:%{http_code}")
  
  http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d':' -f2)
  body=$(echo "$response" | grep -v "HTTP_STATUS")
  
  echo "HTTP Status: $http_status"
  
  # Check if response contains token
  if echo "$body" | grep -q '"token"'; then
    echo "✅ SUCCESS - Token found!"
    echo "$body" | head -c 200
    echo "..."
  elif echo "$body" | grep -q '"error"'; then
    echo "❌ ERROR Response:"
    echo "$body" | head -c 300
  else
    echo "Response preview:"
    echo "$body" | head -c 200
  fi
done

echo ""
echo "============================================================"
