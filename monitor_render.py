#!/usr/bin/env python
"""Monitor Render deployment status."""

import urllib.request
import time
import sys

RENDER_URL = "https://toolsora.onrender.com"

endpoints = [
    "/status",
    "/content",
    "/plugins",
    "/dashboard",
]

print("=" * 70)
print("MONITORING RENDER DEPLOYMENT")
print("=" * 70)
print(f"\nTarget: {RENDER_URL}")
print(f"Checking endpoints: {', '.join(endpoints)}\n")

for attempt in range(1, 13):  # Try for up to 2 minutes
    print(f"[Attempt {attempt}/12] Checking server status...")
    
    all_good = True
    for endpoint in endpoints:
        url = f"{RENDER_URL}{endpoint}"
        try:
            response = urllib.request.urlopen(url, timeout=5)
            status = response.status
            content_length = len(response.read())
            
            if status == 200:
                print(f"  OK  {endpoint:20} ({content_length} bytes)")
            else:
                print(f"  ERR {endpoint:20} (Status {status})")
                all_good = False
        except Exception as e:
            print(f"  ERR {endpoint:20} ({str(e)[:40]})")
            all_good = False
    
    if all_good:
        print("\n" + "=" * 70)
        print("SUCCESS! All endpoints are responding correctly.")
        print("=" * 70)
        sys.exit(0)
    
    if attempt < 12:
        print(f"  Waiting 10 seconds before retry...\n")
        time.sleep(10)

print("\n" + "=" * 70)
print("TIMEOUT: Server did not respond within 2 minutes")
print("Check Render dashboard for deployment errors")
print("=" * 70)
sys.exit(1)
