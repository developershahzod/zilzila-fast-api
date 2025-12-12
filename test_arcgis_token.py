#!/usr/bin/env python3
"""
Test script to verify ArcGIS token generation
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.arcgis_sync_scheduler import get_arcgis_token

if __name__ == "__main__":
    print("=" * 60)
    print("Testing ArcGIS Token Generation")
    print("=" * 60)
    print()
    
    token = get_arcgis_token()
    
    print()
    print("=" * 60)
    if token:
        print("✅ SUCCESS: Token obtained!")
        print(f"Token length: {len(token)} characters")
        print(f"Token preview: {token[:50]}...")
    else:
        print("❌ FAILED: Could not obtain token")
        print("Check the logs above for details")
    print("=" * 60)
