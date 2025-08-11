import requests
import json

def test_incidents_with_gares():
    try:
        # Tester l'API des incidents
        response = requests.get('http://localhost:5000/api/evenements?per_page=5')
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                incidents = data['data']
                print(f"✅ {len(incidents)} incidents récupérés")
                
                # Tester l'API des gares pour récupérer les coordonnées
                gares_response = requests.get('http://localhost:5000/api/gares')
                gares_data = {}
                
                if gares_response.status_code == 200:
                    gares_json = gares_response.json()
                    if gares_json['success']:
                        for gare in gares_json['data']:
                            gares_data[gare['code']] = gare
                        print(f"✅ {len(gares_data)} gares récupérées")
                
                print("\nAnalyse des incidents avec leurs gares:")
                for i, incident in enumerate(incidents, 1):
                    print(f"\n--- Incident {i} ---")
                    print(f"ID: {incident['id']}")
                    print(f"Description: {incident['description'][:100]}...")
                    print(f"Gare début: {incident['gare_debut_id']}")
                    print(f"Gare fin: {incident['gare_fin_id']}")
                    
                    # Vérifier si on a les coordonnées des gares
                    if incident['gare_debut_id'] and incident['gare_debut_id'] in gares_data:
                        gare = gares_data[incident['gare_debut_id']]
                        print(f"✅ Coordonnées gare début trouvées: {gare['geometrie'][:50]}...")
                    elif incident['gare_fin_id'] and incident['gare_fin_id'] in gares_data:
                        gare = gares_data[incident['gare_fin_id']]
                        print(f"✅ Coordonnées gare fin trouvées: {gare['geometrie'][:50]}...")
                    else:
                        print("❌ Aucune coordonnée de gare trouvée")
                    
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_incidents_with_gares() 