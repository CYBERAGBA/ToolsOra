#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test rapide des 6 nouveaux modules
"""
import sys
sys.path.insert(0, '/c/Users/Monsieur AGBA/Desktop/orahub')

from app import create_app

app = create_app()

# Vérifier les routes enregistrées
print("=" * 80)
print("ROUTES ENREGISTRÉES DANS L'APPLICATION FLASK")
print("=" * 80)

routes = []
for rule in app.url_map.iter_rules():
    if 'modules' in str(rule):
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(rule.methods - {'OPTIONS', 'HEAD'}),
            'route': str(rule)
        })

# Grouper par module
modules = {}
for route in routes:
    module = route['route'].split('/')[2] if len(route['route'].split('/')) > 2 else 'unknown'
    if module not in modules:
        modules[module] = []
    modules[module].append(route)

for module in sorted(modules.keys()):
    print(f"\n📦 Module: {module.upper()}")
    print("-" * 80)
    for route in modules[module]:
        print(f"  {route['route']:40} [{route['methods']}]")

print("\n" + "=" * 80)
print("✅ TEMPLATES CRÉÉS")
print("=" * 80)

templates = [
    '/templates/aiml.html',
    '/templates/sms.html', 
    '/templates/export.html',
    '/templates/notifications.html',
    '/templates/rewards.html',
    '/templates/scheduling.html'
]

import os
base_path = '/c/Users/Monsieur AGBA/Desktop/orahub'

for template in templates:
    full_path = base_path + template
    exists = "✅" if os.path.exists(full_path) else "❌"
    print(f"{exists} {template}")

print("\n" + "=" * 80)
print("Flask app successfully created!")
print("=" * 80)
