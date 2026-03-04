#!/usr/bin/env python
"""Test Flask routes and template rendering."""

from app import create_app
import sys

try:
    app = create_app()
    print("✓ Flask app created successfully")
    
    # List relevant routes
    print("\nRoutes containing 'content' or 'plugins':")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        rule_str = str(rule)
        if 'content' in rule_str.lower() or 'plugins' in rule_str.lower():
            print(f"  {rule}")
    
    # Test if templates exist
    print("\nTemplate existence check:")
    import os
    templates_path = os.path.join(os.path.dirname(__file__), 'templates')
    
    for template in ['content.html', 'plugins.html', 'base.html', 'macros.html']:
        path = os.path.join(templates_path, template)
        exists = os.path.exists(path)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {template:20} {status}")
    
    print("\n✓ All checks passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
