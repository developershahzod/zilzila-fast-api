#!/usr/bin/env python3
"""
Test script to debug ArcGIS authentication
"""

import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
USERNAME = "zilzila"
PASSWORD = "zilzila@6739space"

print("=" * 60)
print("ArcGIS Authentication Test")
print("=" * 60)

# Test URLs to try
urls_to_try = [
    "https://gis.uzspace.uz/portal/sharing/rest/generateToken",
    "https://gis.uzspace.uz/uzspacesrvr/sharing/rest/generateToken",
    "https://gis.uzspace.uz/server/rest/generateToken",
    "https://gis.uzspace.uz/arcgis/sharing/rest/generateToken",
]

for url in urls_to_try:
    print(f"\n🔑 Testing: {url}")
    print("-" * 60)
    
    # Try different parameter combinations
    param_sets = [
        {
            "username": USERNAME,
            "password": PASSWORD,
            "client": "referer",
            "referer": "https://gis.uzspace.uz",
            "expiration": 60,
            "f": "json"
        },
        {
            "username": USERNAME,
            "password": PASSWORD,
            "referer": "https://gis.uzspace.uz",
            "f": "json"
        },
        {
            "username": USERNAME,
            "password": PASSWORD,
            "f": "json"
        }
    ]
    
    for i, params in enumerate(param_sets, 1):
        try:
            print(f"\n  Attempt {i}: {list(params.keys())}")
            response = requests.post(url, data=params, timeout=10, verify=False)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "token" in result:
                        print(f"  ✅ SUCCESS! Token obtained")
                        print(f"  Token (first 50 chars): {result['token'][:50]}...")
                        print(f"\n✅ Working configuration found!")
                        print(f"  URL: {url}")
                        print(f"  Params: {json.dumps(params, indent=2)}")
                        exit(0)
                    elif "error" in result:
                        print(f"  ❌ Error: {result['error']}")
                    else:
                        print(f"  ⚠️  Response: {json.dumps(result, indent=2)[:200]}")
                except:
                    print(f"  ⚠️  Non-JSON response: {response.text[:200]}")
            else:
                print(f"  ❌ HTTP Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

print("\n" + "=" * 60)
print("❌ No working configuration found")
print("=" * 60)
print("\nPossible issues:")
print("1. Incorrect credentials")
print("2. Server requires different authentication method")
print("3. Network/firewall blocking access")
print("4. Server endpoint has changed")
print("\nNext steps:")
print("1. Verify credentials with ArcGIS admin")
print("2. Check ArcGIS server documentation")
print("3. Test from ArcGIS Portal web interface")
