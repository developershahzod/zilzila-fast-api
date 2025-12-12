#!/bin/bash
# Test the correct ArcGIS token generation endpoint

echo "============================================================"
echo "Testing ArcGIS Token Generation - FINAL"
echo "============================================================"
echo ""
echo "Endpoint: https://gis.uzspace.uz/uzspace/sharing/rest/generateToken"
echo "Username: zilzila"
echo "Client: referer"
echo "Referer: https://api-zilzila.spacemc.uz/"
echo "Expiration: 20160 minutes (14 days)"
echo ""
echo "------------------------------------------------------------"

curl -k -X POST "https://gis.uzspace.uz/uzspace/sharing/rest/generateToken" \
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" \
  -H "accept-language: ru-RU,ru;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6" \
  -H "cache-control: no-cache" \
  -H "content-type: application/x-www-form-urlencoded" \
  -H "pragma: no-cache" \
  --data-urlencode "username=zilzila" \
  --data-urlencode "password=zilzila@6739space" \
  --data-urlencode "client=referer" \
  --data-urlencode "referer=https://api-zilzila.spacemc.uz/" \
  --data-urlencode "expiration=20160" \
  --data-urlencode "f=json" \
  --max-time 10 | python3 -m json.tool 2>/dev/null || cat

echo ""
echo ""
echo "============================================================"
