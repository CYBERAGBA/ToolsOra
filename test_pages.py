#!/usr/bin/env python
"""Quick test to render content and plugins pages."""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

try:
    app = create_app()
    
    with app.test_client() as client:
        print("Testing /content endpoint...")
        response = client.get('/content')
        print(f"  Status: {response.status_code}")
        content_length = len(response.data)
        print(f"  Content length: {content_length} bytes")
        
        if response.status_code == 200:
            if content_length < 1000:
                print("  ⚠ WARNING: Content length is very small!")
                print("  First 500 chars:")
                print(response.data[:500])
            else:
                print("  ✓ Content page looks good")
                # Check for key content
                if b'Content Hub' in response.data and b'article' in response.data.lower():
                    print("  ✓ Contains expected content")
                else:
                    print("  ⚠ Missing expected content")
        else:
            print(f"  ✗ Error: {response.status_code}")
            print(f"  Response: {response.data}")
            sys.exit(1)
        
        print("\nTesting /plugins endpoint...")
        response = client.get('/plugins')
        print(f"  Status: {response.status_code}")
        content_length = len(response.data)
        print(f"  Content length: {content_length} bytes")
        
        if response.status_code == 200:
            if content_length < 1000:
                print("  ⚠ WARNING: Content length is very small!")
                print("  First 500 chars:")
                print(response.data[:500])
            else:
                print("  ✓ Plugins page looks good")
                # Check for key content
                if b'Plugins' in response.data or b'plugin' in response.data.lower():
                    print("  ✓ Contains expected content")
                else:
                    print("  ⚠ Missing expected content")
        else:
            print(f"  ✗ Error: {response.status_code}")
            print(f"  Response: {response.data}")
            sys.exit(1)
    
    print("\n✓ Both pages render successfully!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
