import requests
import json

def check_gare_codes():
    try:
        # Récupérer toutes les gares
        gares_response = requests.get('http://localhost:5000/api/gares')
        
        if gares_response.status_code == 200:
            gares_json = gares_response.json()
            if gares_json['success']:
                gares = gares_json['data']
                print(f"✅ {len(gares)} gares récupérées")
                
                # Afficher les codes de gares disponibles
                print("\nCodes de gares disponibles:")
                for gare in gares[:10]:  # Afficher les 10 premiers
                    print(f"  - {gare['code']}: {gare['nom']}")
                
                # Récupérer quelques incidents
                incidents_response = requests.get('http://localhost:5000/api/evenements?per_page=5')
                if incidents_response.status_code == 200:
                    incidents_json = incidents_response.json()
                    if incidents_json['success']:
                        incidents = incidents_json['data']
                        
                        print("\nCodes de gares dans les incidents:")
                        for incident in incidents:
                            if incident['gare_debut_id']:
                                print(f"  - {incident['gare_debut_id']}")
                            if incident['gare_fin_id']:
                                print(f"  - {incident['gare_fin_id']}")
                        
                        # Vérifier les correspondances
                        gare_codes = {gare['code'] for gare in gares}
                        incident_gare_codes = set()
                        
                        for incident in incidents:
                            if incident['gare_debut_id']:
                                incident_gare_codes.add(incident['gare_debut_id'])
                            if incident['gare_fin_id']:
                                incident_gare_codes.add(incident['gare_fin_id'])
                        
                        print(f"\nCodes de gares dans les incidents: {len(incident_gare_codes)}")
                        print(f"Codes de gares dans la table gares: {len(gare_codes)}")
                        
                        # Trouver les correspondances
                        correspondances = gare_codes.intersection(incident_gare_codes)
                        print(f"Correspondances trouvées: {len(correspondances)}")
                        
                        if correspondances:
                            print("Codes correspondants:")
                            for code in list(correspondances)[:5]:
                                print(f"  - {code}")
                        
                        # Codes non trouvés
                        non_trouves = incident_gare_codes - gare_codes
                        if non_trouves:
                            print(f"\nCodes non trouvés dans la table gares ({len(non_trouves)}):")
                            for code in list(non_trouves)[:10]:
                                print(f"  - {code}")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_gare_codes() 