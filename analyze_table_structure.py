#!/usr/bin/env python3
"""
Analyser la structure exacte des tables pour corriger les modèles SQLAlchemy
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_table_columns(table_schema, table_name):
    """Analyser les colonnes d'une table"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_schema, table_name))
        
        columns = cursor.fetchall()
        
        print(f"\n📋 Structure de {table_schema}.{table_name}")
        print("-" * 60)
        
        for col_name, data_type, nullable, default in columns:
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"   {col_name:<20} {data_type:<20} {nullable_str}{default_str}")
        
        return columns
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def main():
    print("🔍 Analyse de la structure des tables")
    print("=" * 60)
    
    # Tables importantes à analyser
    tables = [
        ('gpr', 'ge_evenement'),
        ('gpr', 'ref_types'),
        ('gpr', 'ge_localisation'),
        ('gpr', 'ref_sous_types')
    ]
    
    for schema, table in tables:
        analyze_table_columns(schema, table)

if __name__ == "__main__":
    main()