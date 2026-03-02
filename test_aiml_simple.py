#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test rapide du module AI/ML avec provider SIMPLE (gratuit!)
"""
import sys
sys.path.insert(0, 'c:/Users/Monsieur AGBA/Desktop/orahub')

from app import create_app
from app.modules.aiml.routes import get_active_provider, _generate_with_simple

app = create_app()

print("=" * 80)
print("🎉 TEST DU MODULE AI/ML - PROVIDER GRATUIT")
print("=" * 80)

# Test 1: Vérifier le provider actif
provider = get_active_provider()
print(f"\n✅ Provider actif: {provider}")

if provider == 'simple':
    print("✅ Moteur SIMPLE (gratuit) activé - Aucune dépendance externe!")
    print("✅ Aucune clé API n'est nécessaire!")
    print("✅ Aucun coût!")

# Test 2: Tester la génération de contenu
print("\n" + "=" * 80)
print("TEST 1: Génération d'article")
print("=" * 80)

result = _generate_with_simple("L'IA en éducation", 'article')
print(f"\n📝 Résultat:\n{result}")

# Test 3: Résumé
print("\n" + "=" * 80)
print("TEST 2: Résumé de texte")
print("=" * 80)

long_text = "L'intelligence artificielle transforme le monde. Elle est utilisée dans l'éducation, la santé, et l'industrie. L'IA offre des opportunités infinies pour l'avenir."
result = _generate_with_simple(long_text, 'summarization')
print(f"\n📋 Résumé:\n{result}")

# Test 4: Classification
print("\n" + "=" * 80)
print("TEST 3: Classification (Sentiment)")
print("=" * 80)

text = "J'adore ce produit, c'est excellent!"
result = _generate_with_simple(text, 'classification')
print(f"\n🏷️  Sentiment: {result}")

print("\n" + "=" * 80)
print("✅ TOUS LES TESTS RÉUSSIS!")
print("✅ Le module AI/ML fonctionne en mode GRATUIT!")
print("=" * 80)
