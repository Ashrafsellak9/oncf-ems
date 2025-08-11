#!/usr/bin/env python3
"""
Script pour corriger l'affichage des vraies données
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_real_data():
    """Corriger l'affichage des vraies données"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🔧 Correction de l'affichage des vraies données")
        print("=" * 60)
        
        # 1. Vérifier les vraies tables
        print("\n📋 Vérification des vraies tables:")
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM "public"."gpr.gpd_gares_ref") as gares_count,
                   (SELECT COUNT(*) FROM "public"."gpr.graphe_arc") as arcs_count
            FROM information_schema.tables 
            WHERE table_name IN ('gpr.gpd_gares_ref', 'gpr.graphe_arc')
            ORDER BY table_name;
        """)
        
        results = cursor.fetchall()
        for table_name, gares_count, arcs_count in results:
            print(f"   - {table_name}: {gares_count} gares, {arcs_count} arcs")
        
        # 2. Supprimer les tables de test si elles existent
        print("\n🗑️  Suppression des tables de test:")
        cursor.execute("DROP TABLE IF EXISTS gpr.gpd_gares_ref CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS gpr.graphe_arc CASCADE;")
        print("   ✅ Tables de test supprimées")
        
        # 3. Créer les vraies tables dans le bon schéma
        print("\n📋 Création des vraies tables:")
        
        # Copier la table des gares
        cursor.execute("""
            CREATE TABLE gpr.gpd_gares_ref AS 
            SELECT * FROM "public"."gpr.gpd_gares_ref";
        """)
        print("   ✅ Table gpr.gpd_gares_ref créée")
        
        # Copier la table des arcs
        cursor.execute("""
            CREATE TABLE gpr.graphe_arc AS 
            SELECT * FROM "public"."gpr.graphe_arc";
        """)
        print("   ✅ Table gpr.graphe_arc créée")
        
        # 4. Créer les index
        print("\n🔍 Création des index:")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_axe ON gpr.gpd_gares_ref(axe);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_gares_type ON gpr.gpd_gares_ref(typegare);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gpr_arcs_axe ON gpr.graphe_arc(axe);")
        print("   ✅ Index créés")
        
        conn.commit()
        
        # 5. Vérifier les résultats
        print("\n📊 Vérification finale:")
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        gares_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        arcs_count = cursor.fetchone()[0]
        
        print(f"   - Gares: {gares_count:,} enregistrements")
        print(f"   - Arcs: {arcs_count:,} enregistrements")
        
        # 6. Afficher quelques exemples
        print("\n📋 Exemples de vraies données:")
        
        cursor.execute("SELECT axe, nomgarefr, typegare, etat FROM gpr.gpd_gares_ref LIMIT 5;")
        gares = cursor.fetchall()
        for gare in gares:
            print(f"   - {gare[1]} ({gare[0]}) | Type: {gare[2]} | État: {gare[3]}")
        
        cursor.execute("SELECT axe, plod, plof, cumulf FROM gpr.graphe_arc LIMIT 3;")
        arcs = cursor.fetchall()
        for arc in arcs:
            print(f"   - {arc[0]}: {arc[1]} → {arc[2]} (PK {arc[3]})")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Correction terminée!")
        print("Les vraies données sont maintenant disponibles dans l'application.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    fix_real_data() 