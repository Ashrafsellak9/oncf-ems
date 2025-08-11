import psycopg2
from psycopg2.extras import RealDictCursor

try:
    # Connexion à la base de données
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/oncf_gis')
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Vérifier les colonnes de la table ge_evenement
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'gpr' AND table_name = 'ge_evenement' 
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print("Colonnes de la table gpr.ge_evenement:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']}")
    
    # Vérifier si il y a des colonnes géométriques
    geometry_columns = [col for col in columns if 'geometry' in col['data_type'].lower()]
    if geometry_columns:
        print(f"\nColonnes géométriques trouvées: {[col['column_name'] for col in geometry_columns]}")
    else:
        print("\nAucune colonne géométrique trouvée")
    
    # Vérifier quelques enregistrements
    cur.execute("SELECT * FROM gpr.ge_evenement LIMIT 3")
    incidents = cur.fetchall()
    
    print(f"\nExemple d'incidents (3 premiers):")
    for i, incident in enumerate(incidents, 1):
        print(f"\nIncident {i}:")
        for key, value in incident.items():
            print(f"  {key}: {value}")
    
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}") 