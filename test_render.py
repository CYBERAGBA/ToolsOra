#!/usr/bin/env python
"""Test Flask routes locally."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()

print("=" * 60)
print("TESTING FLASK ROUTES")
print("=" * 60)

print("\nAll registered routes:")
print("-" * 60)
for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    if 'content' in str(rule).lower() or 'plugins' in str(rule).lower():
        print(f"{str(rule):40} [{methods}]")

print("\n\nTesting page rendering with test client:")
print("-" * 60)

with app.test_client() as client:
    for endpoint, path in [('content', '/content'), ('plugins', '/plugins')]:
        print(f"\nTesting {endpoint}: GET {path}")
        try:
            response = client.get(path)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   OK - {len(response.data)} bytes")
                if endpoint == 'content':
                    if b'Content Hub' in response.data:
                        print(f"   OK - Contains 'Content Hub'")
                    elif b'content' in response.data:
                        print(f"   OK - Contains 'content'")
                elif endpoint == 'plugins':
                    if b'Plugins' in response.data:
                        print(f"   OK - Contains 'Plugins'")
                    elif b'OpenAI' in response.data:
                        print(f"   OK - Contains 'OpenAI'")
            else:
                print(f"   ERROR - Status {response.status_code}")
                print(f"   Response: {response.data[:200]}")
        except Exception as e:
            print(f"   EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
