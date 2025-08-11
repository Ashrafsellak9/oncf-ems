import requests
import json

def test_map_display():
    try:
        print("🔍 Test de l'affichage sur la carte interactive")
        print("=" * 50)
        
        # Test des gares
        print("\n1. Test des gares:")
        gares_response = requests.get('http://localhost:5000/api/gares')
        if gares_response.status_code == 200:
            gares_data = gares_response.json()
            if gares_data['success']:
                gares = gares_data['data']
                print(f"✅ {len(gares)} gares récupérées")
                
                # Vérifier les coordonnées des gares
                gares_with_coords = [g for g in gares if g.get('geometrie')]
                print(f"✅ {len(gares_with_coords)} gares avec coordonnées")
                
                if gares_with_coords:
                    first_gare = gares_with_coords[0]
                    print(f"   Exemple: {first_gare['nom']} - {first_gare['geometrie'][:50]}...")
            else:
                print("❌ Erreur API gares")
        else:
            print(f"❌ Erreur HTTP gares: {gares_response.status_code}")
        
        # Test des incidents
        print("\n2. Test des incidents:")
        incidents_response = requests.get('http://localhost:5000/api/evenements?per_page=10')
        if incidents_response.status_code == 200:
            incidents_data = incidents_response.json()
            if incidents_data['success']:
                incidents = incidents_data['data']
                print(f"✅ {len(incidents)} incidents récupérés")
                
                # Vérifier les coordonnées des incidents
                incidents_with_coords = [i for i in incidents if i.get('geometrie')]
                print(f"✅ {len(incidents_with_coords)} incidents avec coordonnées")
                
                if incidents_with_coords:
                    first_incident = incidents_with_coords[0]
                    print(f"   Exemple: Incident #{first_incident['id']} - {first_incident['geometrie']}")
                    print(f"   Localisation: {first_incident.get('location_name', 'N/A')}")
            else:
                print("❌ Erreur API incidents")
        else:
            print(f"❌ Erreur HTTP incidents: {incidents_response.status_code}")
        
        # Test des arcs
        print("\n3. Test des arcs:")
        arcs_response = requests.get('http://localhost:5000/api/arcs')
        if arcs_response.status_code == 200:
            arcs_data = arcs_response.json()
            if arcs_data['success']:
                arcs = arcs_data['data']
                print(f"✅ {len(arcs)} arcs récupérés")
                
                # Vérifier les coordonnées des arcs
                arcs_with_coords = [a for a in arcs if a.get('geometrie')]
                print(f"✅ {len(arcs_with_coords)} arcs avec coordonnées")
                
                if arcs_with_coords:
                    first_arc = arcs_with_coords[0]
                    print(f"   Exemple: {first_arc['axe']} - {first_arc['geometrie'][:50]}...")
            else:
                print("❌ Erreur API arcs")
        else:
            print(f"❌ Erreur HTTP arcs: {arcs_response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 Résumé:")
        print("- Les gares devraient s'afficher avec des marqueurs colorés")
        print("- Les incidents devraient s'afficher avec des marqueurs rouges")
        print("- Les arcs devraient s'afficher comme des lignes colorées")
        print("- Utilisez les filtres pour afficher/masquer les différentes couches")
        print("- Les incidents ont une pagination avec boutons Précédent/Suivant")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_map_display() 