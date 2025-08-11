#!/usr/bin/env python3
"""
Script pour tester les API et voir quelles données sont retournées
"""

import requests
import json

def test_api_endpoint(endpoint, name):
    """Tester un endpoint API"""
    try:
        url = f"http://localhost:5000{endpoint}"
        print(f"\n🔍 Test de {name} ({endpoint})")
        print("-" * 50)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statut: {response.status_code}")
            print(f"📊 Réponse: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            
            if 'data' in data and isinstance(data['data'], list):
                print(f"📈 Nombre d'éléments: {len(data['data'])}")
            
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")

def main():
    print("🚂 Test des API ONCF GIS")
    print("=" * 60)
    
    # Tester tous les endpoints
    endpoints = [
        ("/api/statistiques", "Statistiques"),
        ("/api/evenements", "Événements"),
        ("/api/types-incidents", "Types d'incidents"),
        ("/api/localisations", "Localisations"),
        ("/api/gares", "Gares"),
        ("/api/arcs", "Arcs")
    ]
    
    for endpoint, name in endpoints:
        test_api_endpoint(endpoint, name)
    
    print(f"\n🎯 Résumé des tests terminé")

if __name__ == "__main__":
    main()