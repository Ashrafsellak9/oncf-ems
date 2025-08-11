#!/usr/bin/env python3
"""
Script pour tester l'API des incidents et vérifier la pagination
"""

import requests
import json

def test_incidents_api():
    """Tester l'API des incidents"""
    base_url = "http://localhost:5000"
    
    print("🧪 Test de l'API des incidents")
    print("=" * 50)
    
    # Test 1: Récupérer tous les incidents
    print("\n1️⃣ Test: Récupération de tous les incidents")
    try:
        response = requests.get(f"{base_url}/api/evenements?per_page=348")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                total_incidents = data['pagination']['total']
                returned_incidents = len(data['data'])
                print(f"✅ Succès: {returned_incidents} incidents retournés sur {total_incidents} au total")
                print(f"   📊 Pagination: {data['pagination']}")
                
                # Afficher quelques exemples d'incidents
                print(f"\n   📋 Exemples d'incidents:")
                for i, incident in enumerate(data['data'][:3]):
                    print(f"      {i+1}. ID: {incident['id']}, Statut: {incident['statut']}, Description: {incident['description'][:50]}...")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: Test de pagination
    print("\n2️⃣ Test: Pagination des incidents")
    try:
        response = requests.get(f"{base_url}/api/evenements?per_page=50&page=1")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Page 1: {len(data['data'])} incidents sur {data['pagination']['total']} au total")
                print(f"   📊 Pages totales: {data['pagination']['pages']}")
                
                # Test page 2
                response2 = requests.get(f"{base_url}/api/evenements?per_page=50&page=2")
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2['success']:
                        print(f"✅ Page 2: {len(data2['data'])} incidents")
                    else:
                        print(f"❌ Erreur page 2: {data2.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Test avec filtres
    print("\n3️⃣ Test: Filtrage des incidents")
    try:
        response = requests.get(f"{base_url}/api/evenements?per_page=100&statut=ACTIVE")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Incidents ACTIVE: {len(data['data'])} incidents trouvés")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    test_incidents_api() 