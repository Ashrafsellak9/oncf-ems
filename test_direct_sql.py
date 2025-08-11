#!/usr/bin/env python3
"""
Test direct avec SQL brut pour vérifier les données
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_direct_queries():
    """Tester les requêtes SQL directement"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🔍 Test des requêtes SQL directes")
        print("=" * 50)
        
        # Test des événements
        print("\n📊 Test gpr.ge_evenement:")
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_evenement;")
        count = cursor.fetchone()[0]
        print(f"   Total: {count:,} événements")
        
        if count > 0:
            cursor.execute("""
                SELECT id, date_debut, etat, resume, type_id 
                FROM gpr.ge_evenement 
                LIMIT 3;
            """)
            events = cursor.fetchall()
            for event in events:
                print(f"   - ID {event[0]}: {event[1]} | {event[2]} | {event[3][:50] if event[3] else 'Pas de résumé'}...")
        
        # Test des types
        print("\n📊 Test gpr.ref_types:")
        cursor.execute("SELECT COUNT(*) FROM gpr.ref_types;")
        count = cursor.fetchone()[0]
        print(f"   Total: {count:,} types")
        
        if count > 0:
            cursor.execute("""
                SELECT id, intitule, etat 
                FROM gpr.ref_types 
                WHERE etat = true 
                LIMIT 5;
            """)
            types = cursor.fetchall()
            for type_inc in types:
                print(f"   - ID {type_inc[0]}: {type_inc[1]} | Actif: {type_inc[2]}")
        
        # Test des localisations
        print("\n📊 Test gpr.ge_localisation:")
        cursor.execute("SELECT COUNT(*) FROM gpr.ge_localisation;")
        count = cursor.fetchone()[0]
        print(f"   Total: {count:,} localisations")
        
        if count > 0:
            cursor.execute("""
                SELECT id, type_localisation, pk_debut, pk_fin, commentaire 
                FROM gpr.ge_localisation 
                LIMIT 3;
            """)
            locs = cursor.fetchall()
            for loc in locs:
                print(f"   - ID {loc[0]}: {loc[1]} | PK {loc[2]}-{loc[3]} | {loc[4][:30] if loc[4] else 'Pas de commentaire'}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_direct_queries()