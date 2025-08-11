#!/usr/bin/env python3
"""
Script pour vérifier le contenu exact de la base de données
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_all_tables():
    """Vérifier toutes les tables et leurs données"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🔍 Vérification complète de la base de données")
        print("=" * 60)
        
        # Lister toutes les tables avec détails
        cursor.execute("""
            SELECT table_schema, table_name,
                   COALESCE((SELECT n_tup_ins FROM pg_stat_user_tables 
                            WHERE schemaname = table_schema AND relname = table_name), 0) as row_count
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"📊 Tables trouvées ({len(tables)} au total):")
        print("-" * 60)
        
        for schema, table, count in tables:
            print(f"   {schema}.{table} : {count:,} enregistrements")
            
            # Pour les tables importantes, afficher quelques exemples
            if table in ['gpd_gares_ref', 'graphe_arc', 'ge_evenement'] and count > 0:
                try:
                    cursor.execute(f"SELECT * FROM {schema}.{table} LIMIT 2;")
                    sample_rows = cursor.fetchall()
                    
                    # Obtenir les noms des colonnes
                    cursor.execute(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_schema = '{schema}' AND table_name = '{table}'
                        ORDER BY ordinal_position;
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    print(f"      Colonnes: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
                    print(f"      Exemple: {sample_rows[0][:3] if sample_rows else 'Aucune donnée'}")
                except Exception as e:
                    print(f"      ⚠️  Erreur lecture: {e}")
                print()
        
        # Vérifier spécifiquement le schéma gpr
        print("\n🎯 Focus sur le schéma gpr:")
        print("-" * 30)
        
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_schema = 'gpr' AND table_name = t.table_name) as col_count
            FROM information_schema.tables t
            WHERE table_schema = 'gpr'
            ORDER BY table_name;
        """)
        
        gpr_tables = cursor.fetchall()
        for table, col_count in gpr_tables:
            cursor.execute(f"SELECT COUNT(*) FROM gpr.{table};")
            row_count = cursor.fetchone()[0]
            print(f"   gpr.{table} : {row_count:,} lignes, {col_count} colonnes")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    check_all_tables()