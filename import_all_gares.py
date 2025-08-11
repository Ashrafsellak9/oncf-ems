#!/usr/bin/env python3
"""
Script pour importer toutes les gares depuis le fichier CSV
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def import_all_gares():
    """Importer toutes les gares depuis le fichier CSV"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🚂 Import de toutes les gares depuis le CSV")
        print("=" * 60)
        
        # 1. Lire le fichier CSV
        csv_file = "sql_data/gpd_gares_ref"
        print(f"\n📋 Lecture du fichier: {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"   ✅ {len(lines)} lignes lues")
        
        # 2. Supprimer la table existante
        print("\n🗑️  Suppression de la table existante:")
        cursor.execute("DROP TABLE IF EXISTS gpr.gpd_gares_ref CASCADE;")
        print("   ✅ Table supprimée")
        
        # 3. Créer la nouvelle table avec la structure complète
        print("\n📋 Création de la nouvelle table:")
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref (
                id SERIAL PRIMARY KEY,
                axe TEXT,
                plod TEXT,
                absd TEXT,
                geometrie geometry(Point, 3857),
                geometrie_dec geometry(Point, 3857),
                codegare TEXT,
                codeoperationnel TEXT,
                codereseau TEXT,
                nomgarefr TEXT,
                typegare TEXT,
                publishid TEXT,
                sivtypegare TEXT,
                num_pk TEXT,
                idville INTEGER,
                villes_ville TEXT,
                etat TEXT
            );
        """)
        print("   ✅ Table créée")
        
        # 4. Importer les données
        print("\n📥 Import des données:")
        for i, line in enumerate(lines, 1):
            if i % 20 == 0:
                print(f"   Progression: {i}/{len(lines)} gares")
            
            # Parser la ligne CSV
            parts = line.strip().split(',')
            if len(parts) >= 17:
                try:
                    cursor.execute("""
                        INSERT INTO gpr.gpd_gares_ref 
                        (axe, plod, absd, geometrie, geometrie_dec, codegare, codeoperationnel, 
                         codereseau, nomgarefr, typegare, publishid, sivtypegare, num_pk, idville, villes_ville, etat)
                        VALUES (%s, %s, %s, ST_GeomFromEWKT(%s), ST_GeomFromEWKT(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        parts[1] if len(parts) > 1 else None,  # axe
                        parts[2] if len(parts) > 2 else None,  # plod
                        parts[3] if len(parts) > 3 else None,  # absd
                        parts[4] if len(parts) > 4 else None,  # geometrie
                        parts[5] if len(parts) > 5 else None,  # geometrie_dec
                        parts[6] if len(parts) > 6 else None,  # codegare
                        parts[7] if len(parts) > 7 else None,  # codeoperationnel
                        parts[8] if len(parts) > 8 else None,  # codereseau
                        parts[9] if len(parts) > 9 else None,  # nomgarefr
                        parts[10] if len(parts) > 10 else None,  # typegare
                        parts[11] if len(parts) > 11 else None,  # publishid
                        parts[12] if len(parts) > 12 else None,  # sivtypegare
                        parts[13] if len(parts) > 13 else None,  # num_pk
                        int(parts[14]) if len(parts) > 14 and parts[14].isdigit() else None,  # idville
                        parts[15] if len(parts) > 15 else None,  # villes_ville
                        parts[16] if len(parts) > 16 else None   # etat
                    ))
                except Exception as e:
                    print(f"   ⚠️  Erreur ligne {i}: {e}")
                    continue
        
        # 5. Créer les index
        print("\n🔍 Création des index:")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_axe ON gpr.gpd_gares_ref(axe);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_type ON gpr.gpd_gares_ref(typegare);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_nom ON gpr.gpd_gares_ref(nomgarefr);")
        print("   ✅ Index créés")
        
        conn.commit()
        
        # 6. Vérifier les résultats
        print("\n📊 Vérification finale:")
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        total_gares = cursor.fetchone()[0]
        
        cursor.execute("SELECT axe, COUNT(*) FROM gpr.gpd_gares_ref GROUP BY axe ORDER BY COUNT(*) DESC;")
        gares_par_axe = cursor.fetchall()
        
        print(f"   - Total: {total_gares:,} gares importées")
        print(f"   - Répartition par axe:")
        for axe, count in gares_par_axe[:10]:  # Top 10
            print(f"     • {axe}: {count} gares")
        
        # 7. Afficher quelques exemples
        print("\n📋 Exemples de gares importées:")
        cursor.execute("""
            SELECT axe, nomgarefr, typegare, villes_ville 
            FROM gpr.gpd_gares_ref 
            WHERE nomgarefr IS NOT NULL 
            ORDER BY axe, nomgarefr 
            LIMIT 10;
        """)
        exemples = cursor.fetchall()
        for axe, nom, type_gare, ville in exemples:
            print(f"   - {nom} ({axe}) | Type: {type_gare} | Ville: {ville}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Import terminé avec succès!")
        print(f"🎯 {total_gares} gares sont maintenant disponibles dans l'application.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    import_all_gares() 