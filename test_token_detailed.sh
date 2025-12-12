#!/bin/bash
# Detailed test for the working endpoint

echo "============================================================"
echo "Testing ArcGIS Token Generation - Detailed"
echo "============================================================"
echo ""
echo "Endpoint: https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken"
echo "Username: farhodmf"
echo ""

# Test 1: requestip client
echo "Test 1: client=requestip"
echo "------------------------------------------------------------"
curl -k -X POST "https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=farhodmf" \
  -d "password=AQ!SW@de3?" \
  -d "client=requestip" \
  -d "expiration=60" \
  -d "f=json" \
  --max-time 10 | python3 -m json.tool 2>/dev/null || cat

echo ""
echo ""

# Test 2: referer client
echo "Test 2: client=referer"
echo "------------------------------------------------------------"
curl -k -X POST "https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=farhodmf" \
  -d "password=AQ!SW@de3?" \
  -d "client=referer" \
  -d "referer=https://gis.uzspace.uz" \
  -d "expiration=60" \
  -d "f=json" \
  --max-time 10 | python3 -m json.tool 2>/dev/null || cat

echo ""
echo ""

# Test 3: ip client
echo "Test 3: client=ip"
echo "------------------------------------------------------------"
curl -k -X POST "https://gis.uzspace.uz/uzspacesrvr/tokens/generateToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=farhodmf" \
  -d "password=AQ!SW@de3?" \
  -d "client=ip" \
  -d "expiration=60" \
  -d "f=json" \
  --max-time 10 | python3 -m json.tool 2>/dev/null || cat

echo ""
echo "============================================================"
