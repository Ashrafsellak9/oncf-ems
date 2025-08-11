#!/usr/bin/env python3
"""
Script pour tester la page des incidents et vérifier la pagination
"""

import requests
import json
from bs4 import BeautifulSoup

def test_incidents_page():
    """Tester la page des incidents"""
    base_url = "http://localhost:5000"
    
    print("🧪 Test de la page des incidents")
    print("=" * 50)
    
    # Test 1: Accès à la page des incidents
    print("\n1️⃣ Test: Accès à la page des incidents")
    try:
        # D'abord se connecter
        session = requests.Session()
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'remember_me': False
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        if login_response.status_code == 200:
            print("✅ Connexion réussie")
        else:
            print("❌ Échec de la connexion")
            return
        
        # Accéder à la page des incidents
        incidents_response = session.get(f"{base_url}/incidents")
        if incidents_response.status_code == 200:
            print("✅ Page des incidents accessible")
            
            # Analyser le contenu HTML
            soup = BeautifulSoup(incidents_response.text, 'html.parser')
            
            # Vérifier la présence des éléments de pagination
            pagination_controls = soup.find('ul', {'id': 'paginationControls'})
            if pagination_controls:
                print("✅ Contrôles de pagination présents")
            else:
                print("⚠️  Contrôles de pagination non trouvés")
            
            # Vérifier la présence du sélecteur d'éléments par page
            items_per_page_select = soup.find('select', {'id': 'itemsPerPageSelect'})
            if items_per_page_select:
                print("✅ Sélecteur d'éléments par page présent")
                options = items_per_page_select.find_all('option')
                print(f"   📋 Options disponibles: {[opt.get('value') for opt in options]}")
            else:
                print("⚠️  Sélecteur d'éléments par page non trouvé")
            
            # Vérifier la présence des informations de pagination
            pagination_info = soup.find('span', {'id': 'paginationInfo'})
            if pagination_info:
                print("✅ Informations de pagination présentes")
            else:
                print("⚠️  Informations de pagination non trouvées")
                
        else:
            print(f"❌ Erreur HTTP: {incidents_response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: API des incidents avec différents paramètres
    print("\n2️⃣ Test: API des incidents avec pagination")
    try:
        # Test avec 50 incidents par page
        response = session.get(f"{base_url}/api/evenements?per_page=50&page=1")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Page 1 (50 incidents): {len(data['data'])} incidents sur {data['pagination']['total']} au total")
                print(f"   📊 Pages totales: {data['pagination']['pages']}")
                
                # Test page 2
                response2 = session.get(f"{base_url}/api/evenements?per_page=50&page=2")
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2['success']:
                        print(f"✅ Page 2 (50 incidents): {len(data2['data'])} incidents")
                    else:
                        print(f"❌ Erreur page 2: {data2.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Test avec 100 incidents par page
    print("\n3️⃣ Test: API avec 100 incidents par page")
    try:
        response = session.get(f"{base_url}/api/evenements?per_page=100&page=1")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Page 1 (100 incidents): {len(data['data'])} incidents sur {data['pagination']['total']} au total")
                print(f"   📊 Pages totales: {data['pagination']['pages']}")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 4: Test avec tous les incidents
    print("\n4️⃣ Test: API avec tous les incidents")
    try:
        response = session.get(f"{base_url}/api/evenements?per_page=348")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Tous les incidents: {len(data['data'])} incidents retournés")
                print(f"   📊 Pagination: {data['pagination']}")
                
                # Afficher quelques exemples
                print(f"\n   📋 Exemples d'incidents:")
                for i, incident in enumerate(data['data'][:3]):
                    print(f"      {i+1}. ID: {incident['id']}, Statut: {incident['statut']}, Description: {incident['description'][:50]}...")
            else:
                print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    test_incidents_page() 