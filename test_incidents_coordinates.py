import requests
import json

def test_incidents_api():
    try:
        # Tester l'API des incidents
        response = requests.get('http://localhost:5000/api/evenements?per_page=5')
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                incidents = data['data']
                print(f"✅ {len(incidents)} incidents récupérés")
                
                print("\nStructure du premier incident:")
                if incidents:
                    first_incident = incidents[0]
                    for key, value in first_incident.items():
                        print(f"  {key}: {value}")
                
                # Vérifier s'il y a des colonnes géométriques
                geometry_keys = [key for key in first_incident.keys() if 'geo' in key.lower() or 'coord' in key.lower()]
                if geometry_keys:
                    print(f"\n🔍 Colonnes géométriques trouvées: {geometry_keys}")
                else:
                    print("\n❌ Aucune colonne géométrique trouvée")
                
                # Vérifier s'il y a des colonnes de localisation
                location_keys = [key for key in first_incident.keys() if 'loc' in key.lower() or 'gare' in key.lower()]
                if location_keys:
                    print(f"\n📍 Colonnes de localisation trouvées: {location_keys}")
                else:
                    print("\n❌ Aucune colonne de localisation trouvée")
                    
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_incidents_api() 