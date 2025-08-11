import requests
import json

def test_localisations_api():
    try:
        # Tester l'API des localisations
        response = requests.get('http://localhost:5000/api/localisations?per_page=10')
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                localisations = data['data']
                print(f"✅ {len(localisations)} localisations récupérées")
                
                print("\nStructure de la première localisation:")
                if localisations:
                    first_loc = localisations[0]
                    for key, value in first_loc.items():
                        print(f"  {key}: {value}")
                
                # Vérifier s'il y a des colonnes géométriques
                geometry_keys = [key for key in first_loc.keys() if 'geo' in key.lower() or 'coord' in key.lower()]
                if geometry_keys:
                    print(f"\n🔍 Colonnes géométriques trouvées: {geometry_keys}")
                else:
                    print("\n❌ Aucune colonne géométrique trouvée")
                
                # Vérifier s'il y a des colonnes de coordonnées
                coord_keys = [key for key in first_loc.keys() if 'lat' in key.lower() or 'lon' in key.lower() or 'x' in key.lower() or 'y' in key.lower()]
                if coord_keys:
                    print(f"\n📍 Colonnes de coordonnées trouvées: {coord_keys}")
                else:
                    print("\n❌ Aucune colonne de coordonnées trouvée")
                    
            else:
                print(f"❌ Erreur API: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_localisations_api() 