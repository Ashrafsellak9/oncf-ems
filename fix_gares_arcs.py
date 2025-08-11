#!/usr/bin/env python3
"""
Script pour copier spécifiquement les tables gares et arcs depuis le schéma gpr existant
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_database():
    """Connexion à la base de données"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def copy_existing_gpr_tables():
    """Copier les tables gpr existantes vers de nouvelles tables dans le même schéma"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Vérifier si les tables sources existent
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM gpr.gpd_gares_ref) as gares_count,
                   (SELECT COUNT(*) FROM gpr.graphe_arc) as arcs_count
            FROM information_schema.tables 
            WHERE table_schema = 'gpr' AND table_name IN ('gpd_gares_ref', 'graphe_arc')
            ORDER BY table_name;
        """)
        
        results = cursor.fetchall()
        if not results:
            print("⚠️  Tables gpr.gpd_gares_ref et gpr.graphe_arc non trouvées")
            return False
        
        # Supprimer les tables cibles si elles existent
        cursor.execute("DROP TABLE IF EXISTS gpr.gpd_gares_ref_new CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS gpr.graphe_arc_new CASCADE;")
        
        # Copier la table des gares
        print("📋 Copie de gpr.gpd_gares_ref...")
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref_new AS 
            SELECT * FROM gpr.gpd_gares_ref;
        """)
        
        # Copier la table des arcs
        print("📋 Copie de gpr.graphe_arc...")
        cursor.execute("""
            CREATE TABLE gpr.graphe_arc_new AS 
            SELECT * FROM gpr.graphe_arc;
        """)
        
        # Renommer les tables
        cursor.execute("DROP TABLE IF EXISTS gpr.gpd_gares_ref_old CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS gpr.graphe_arc_old CASCADE;")
        
        cursor.execute("ALTER TABLE gpr.gpd_gares_ref RENAME TO gpd_gares_ref_old;")
        cursor.execute("ALTER TABLE gpr.graphe_arc RENAME TO graphe_arc_old;")
        
        cursor.execute("ALTER TABLE gpr.gpd_gares_ref_new RENAME TO gpd_gares_ref;")
        cursor.execute("ALTER TABLE gpr.graphe_arc_new RENAME TO graphe_arc;")
        
        # Créer les index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_axe ON gpr.gpd_gares_ref(axe);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_type ON gpr.gpd_gares_ref(typegare);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_arcs_axe ON gpr.graphe_arc(axe);")
        
        conn.commit()
        
        # Vérifier les résultats
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        gares_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        arcs_count = cursor.fetchone()[0]
        
        print(f"✅ Tables copiées avec succès:")
        print(f"   - Gares: {gares_count:,} enregistrements")
        print(f"   - Arcs: {arcs_count:,} enregistrements")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("🔧 Correction des tables gares et arcs...")
    
    if copy_existing_gpr_tables():
        print("\n✅ Correction terminée!")
        print("Toutes vos données sont maintenant disponibles dans l'application.")
    else:
        print("\n❌ Correction échouée")

if __name__ == "__main__":
    main()