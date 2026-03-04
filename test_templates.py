#!/usr/bin/env python
"""Test template compilation."""

from app import create_app
from jinja2 import TemplateSyntaxError
import sys

try:
    app = create_app()
    
    print("Testing template compilation...")
    with app.app_context():
        # Try to compile templates
        for template_name in ['content.html', 'plugins.html']:
            print(f"\nTesting {template_name}...")
            try:
                template = app.jinja_env.get_template(template_name)
                print(f"  ✓ {template_name} compiled successfully")
            except TemplateSyntaxError as e:
                print(f"  ✗ Syntax error in {template_name}:")
                print(f"    Line {e.lineno}: {e.message}")
                sys.exit(1)
            except Exception as e:
                print(f"  ✗ Error in {template_name}: {e}")
                sys.exit(1)
        
        # Try to render templates with mock context
        from flask import session
        with app.test_request_context():
            print("\nTesting template rendering...")
            for route, template in [('/content', 'content.html'), ('/plugins', 'plugins.html')]:
                try:
                    print(f"\nRendering {route} ({template})...")
                    rendered = app.jinja_env.get_template(template).render()
                    if rendered:
                        length = len(rendered)
                        print(f"  ✓ {template} rendered successfully ({length} bytes)")
                        if length < 500:
                            print(f"  ⚠ Warning: Rendered output is very small ({length} bytes)")
                    else:
                        print(f"  ✗ {template} rendered to empty string!")
                        sys.exit(1)
                except Exception as e:
                    print(f"  ✗ Error rendering {template}: {e}")
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)
    
    print("\n✓ All tests passed!")
    sys.exit(0)

except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
