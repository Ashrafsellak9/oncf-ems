#!/usr/bin/env python3
"""
Script d'importation des données CSV dans PostgreSQL pour ONCF GIS
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import sys

# Charger les variables d'environnement
load_dotenv()

def connect_to_database():
    """Établir la connexion à la base de données PostgreSQL"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)

def create_schema_and_tables(conn):
    """Créer le schéma et les tables nécessaires"""
    cursor = conn.cursor()
    
    try:
        # Créer le schéma GPR
        cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr;")
        
        # Créer la table graphe_arc
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.graphe_arc (
                id SERIAL PRIMARY KEY,
                axe TEXT,
                cumuld NUMERIC,
                cumulf NUMERIC,
                plod TEXT,
                absd NUMERIC,
                plof TEXT,
                absf NUMERIC,
                geometrie geometry(LINESTRING, 3857)
            );
        """)
        
        # Créer la table gpd_gares_ref
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.gpd_gares_ref (
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
        
        conn.commit()
        print("✅ Schéma et tables créés avec succès")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la création des tables: {e}")
        sys.exit(1)
    finally:
        cursor.close()

def import_csv_data(conn, csv_file, table_name):
    """Importer les données CSV dans une table PostgreSQL"""
    cursor = conn.cursor()
    
    try:
        # Lire le fichier CSV
        print(f"📖 Lecture du fichier {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Nettoyer les données
        df = df.fillna('')
        
        # Préparer les données pour l'insertion
        columns = df.columns.tolist()
        data = [tuple(row) for row in df.values]
        
        # Construire la requête d'insertion
        placeholders = ','.join(['%s'] * len(columns))
        query = f"INSERT INTO gpr.{table_name} ({','.join(columns)}) VALUES {placeholders}"
        
        # Insérer les données
        print(f"📥 Importation de {len(data)} enregistrements dans {table_name}...")
        execute_values(cursor, query, data)
        
        conn.commit()
        print(f"✅ {len(data)} enregistrements importés dans {table_name}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'importation de {csv_file}: {e}")
    finally:
        cursor.close()

def import_geometry_data(conn, csv_file, table_name):
    """Importer les données géométriques spéciales"""
    cursor = conn.cursor()
    
    try:
        # Lire le fichier CSV
        print(f"📖 Lecture du fichier {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Nettoyer les données
        df = df.fillna('')
        
        # Traiter chaque ligne
        for index, row in df.iterrows():
            # Préparer les données (exclure la colonne id si elle existe)
            data_columns = [col for col in df.columns if col != 'id']
            data_values = [row[col] for col in data_columns]
            
            # Construire la requête d'insertion
            placeholders = ','.join(['%s'] * len(data_columns))
            query = f"INSERT INTO gpr.{table_name} ({','.join(data_columns)}) VALUES ({placeholders})"
            
            cursor.execute(query, data_values)
        
        conn.commit()
        print(f"✅ {len(df)} enregistrements importés dans {table_name}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'importation de {csv_file}: {e}")
    finally:
        cursor.close()

def create_indexes(conn):
    """Créer les index pour optimiser les performances"""
    cursor = conn.cursor()
    
    try:
        # Index pour graphe_arc
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_graphe_arc_axe ON gpr.graphe_arc(axe);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_graphe_arc_geometrie ON gpr.graphe_arc USING GIST(geometrie);")
        
        # Index pour gpd_gares_ref
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gares_ref_axe ON gpr.gpd_gares_ref(axe);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gares_ref_type ON gpr.gpd_gares_ref(typegare);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gares_ref_etat ON gpr.gpd_gares_ref(etat);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gares_ref_geometrie ON gpr.gpd_gares_ref USING GIST(geometrie);")
        
        conn.commit()
        print("✅ Index créés avec succès")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la création des index: {e}")
    finally:
        cursor.close()

def verify_data(conn):
    """Vérifier les données importées"""
    cursor = conn.cursor()
    
    try:
        # Compter les enregistrements
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        arcs_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        gares_count = cursor.fetchone()[0]
        
        print(f"\n📊 Vérification des données:")
        print(f"   - Sections de voie (graphe_arc): {arcs_count}")
        print(f"   - Gares (gpd_gares_ref): {gares_count}")
        
        # Statistiques par axe
        cursor.execute("SELECT axe, COUNT(*) FROM gpr.gpd_gares_ref GROUP BY axe ORDER BY COUNT(*) DESC;")
        axes_stats = cursor.fetchall()
        
        print(f"\n🏗️  Répartition par axe:")
        for axe, count in axes_stats:
            print(f"   - {axe}: {count} gares")
        
        # Types de gares
        cursor.execute("SELECT typegare, COUNT(*) FROM gpr.gpd_gares_ref GROUP BY typegare ORDER BY COUNT(*) DESC;")
        types_stats = cursor.fetchall()
        
        print(f"\n🏢 Types de gares:")
        for type_gare, count in types_stats:
            print(f"   - {type_gare}: {count} gares")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        cursor.close()

def main():
    """Fonction principale"""
    print("🚂 ONCF GIS - Importation des Données")
    print("=" * 50)
    
    # Vérifier que les fichiers CSV existent
    csv_files = {
        'graphe_arc': 'sql_data/graphe_arc',
        'gpd_gares_ref': 'sql_data/gpd_gares_ref'
    }
    
    for table_name, file_path in csv_files.items():
        if not os.path.exists(file_path):
            print(f"❌ Fichier {file_path} non trouvé")
            sys.exit(1)
    
    # Connexion à la base de données
    print("🔌 Connexion à la base de données...")
    conn = connect_to_database()
    
    try:
        # Créer le schéma et les tables
        print("\n🏗️  Création du schéma et des tables...")
        create_schema_and_tables(conn)
        
        # Vider les tables existantes
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE gpr.graphe_arc RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE gpr.gpd_gares_ref RESTART IDENTITY CASCADE;")
        conn.commit()
        cursor.close()
        print("🧹 Tables vidées")
        
        # Importer les données
        print("\n📥 Importation des données...")
        
        # Importer graphe_arc
        import_csv_data(conn, 'sql_data/graphe_arc', 'graphe_arc')
        
        # Importer gpd_gares_ref
        import_csv_data(conn, 'sql_data/gpd_gares_ref', 'gpd_gares_ref')
        
        # Créer les index
        print("\n🔍 Création des index...")
        create_indexes(conn)
        
        # Vérifier les données
        print("\n✅ Vérification finale...")
        verify_data(conn)
        
        print("\n🎉 Importation terminée avec succès!")
        print("\nVous pouvez maintenant lancer l'application avec:")
        print("   python app.py")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 