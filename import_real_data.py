#!/usr/bin/env python3
"""
Script d'import des vraies données CSV ONCF vers PostgreSQL
Compatible avec Python 3.13
"""

import psycopg2
import psycopg2.extras
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def connect_to_database():
    """Établir une connexion à la base de données PostgreSQL"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def create_schema_and_tables(cursor):
    """Créer le schéma et toutes les tables nécessaires"""
    try:
        # Créer le schéma
        cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr;")
        print("✅ Schéma 'gpr' créé/vérifié")
        
        # Table des gares (structure mise à jour)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.gpd_gares_ref (
                id SERIAL PRIMARY KEY,
                axe TEXT,
                plod TEXT,
                absd TEXT,
                geometrie TEXT,
                geometrie_dec TEXT,
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
        
        # Table des arcs
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
                geometrie TEXT
            );
        """)
        
        # Table des événements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.ge_evenement (
                id SERIAL PRIMARY KEY,
                date_debut TIMESTAMP,
                date_fin TIMESTAMP,
                col3 TEXT,
                col4 TEXT,
                date_creation TIMESTAMP,
                type_id INTEGER,
                statut TEXT,
                heure_debut TIME,
                heure_fin TIME,
                col10 TEXT,
                col11 TEXT,
                col12 BOOLEAN,
                col13 BOOLEAN,
                col14 BOOLEAN,
                col15 BOOLEAN,
                description TEXT
            );
        """)
        
        # Table des types de référence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.ref_types (
                id SERIAL PRIMARY KEY,
                date_creation TIMESTAMP,
                libelle TEXT,
                niveau INTEGER,
                systeme_id INTEGER,
                actif BOOLEAN,
                supprime BOOLEAN
            );
        """)
        
        # Table des localisations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.ge_localisation (
                id SERIAL PRIMARY KEY,
                axe TEXT,
                pk_debut NUMERIC,
                pk_fin NUMERIC,
                voie TEXT,
                section TEXT,
                gare TEXT,
                description TEXT,
                col8 TEXT,
                col9 TEXT,
                col10 TEXT,
                col11 TEXT,
                col12 TEXT,
                col13 TEXT,
                col14 TEXT,
                col15 TEXT,
                col16 TEXT,
                col17 TEXT,
                col18 TEXT,
                col19 TEXT,
                col20 TEXT
            );
        """)
        
        # Table des sous-types
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gpr.ref_sous_types (
                id SERIAL PRIMARY KEY,
                date_creation TIMESTAMP,
                libelle TEXT,
                type_id INTEGER,
                systeme_id INTEGER,
                actif BOOLEAN,
                supprime BOOLEAN,
                col7 TEXT,
                col8 TEXT,
                col9 TEXT,
                col10 TEXT,
                col11 TEXT,
                col12 TEXT,
                col13 TEXT,
                col14 TEXT,
                col15 TEXT,
                col16 TEXT,
                col17 TEXT,
                col18 TEXT,
                col19 TEXT,
                col20 TEXT
            );
        """)
        
        print("✅ Toutes les tables ont été créées/vérifiées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

def parse_datetime(date_str):
    """Parser une date/heure avec gestion des erreurs"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return None

def parse_time(time_str):
    """Parser une heure avec gestion des erreurs"""
    if not time_str or time_str.strip() == '':
        return None
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except:
        return None

def parse_boolean(bool_str):
    """Parser un booléen"""
    if not bool_str or bool_str.strip() == '':
        return None
    return bool_str.lower() in ('t', 'true', '1', 'yes', 'oui')

def import_csv_file(cursor, csv_file, table_name, columns_mapping):
    """Importer un fichier CSV dans une table"""
    csv_path = f"sql_data/{csv_file}"
    
    if not os.path.exists(csv_path):
        print(f"⚠️  Fichier {csv_path} non trouvé, ignoré")
        return 0
    
    try:
        # Vider la table existante
        cursor.execute(f"TRUNCATE TABLE gpr.{table_name} RESTART IDENTITY CASCADE;")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows_inserted = 0
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Préparer les données selon le mapping
                    data = {}
                    for i, (col_name, col_type) in enumerate(columns_mapping.items()):
                        if i < len(row):
                            value = row[i].strip() if row[i] else None
                            
                            if col_type == 'int' and value:
                                data[col_name] = int(value) if value.isdigit() else None
                            elif col_type == 'float' and value:
                                try:
                                    data[col_name] = float(value.replace(',', '.'))
                                except:
                                    data[col_name] = None
                            elif col_type == 'datetime' and value:
                                data[col_name] = parse_datetime(value)
                            elif col_type == 'time' and value:
                                data[col_name] = parse_time(value)
                            elif col_type == 'bool' and value:
                                data[col_name] = parse_boolean(value)
                            else:
                                data[col_name] = value if value else None
                        else:
                            data[col_name] = None
                    
                    # Construire la requête d'insertion
                    columns = list(data.keys())
                    values = list(data.values())
                    
                    placeholders = ', '.join(['%s'] * len(columns))
                    columns_str = ', '.join(columns)
                    
                    query = f"INSERT INTO gpr.{table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                    rows_inserted += 1
                    
                except Exception as e:
                    print(f"⚠️  Erreur ligne {row_num} dans {csv_file}: {e}")
                    continue
        
        print(f"✅ {rows_inserted} lignes importées dans {table_name}")
        return rows_inserted
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import de {csv_file}: {e}")
        return 0

def import_all_data():
    """Importer toutes les données CSV"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Créer les tables
        if not create_schema_and_tables(cursor):
            return False
        
        print("\n📊 Import des données CSV...")
        
        # Configuration des mappings pour chaque fichier
        mappings = {
            'gpd_gares_ref': {
                'id': 'int',
                'axe': 'str',
                'plod': 'str', 
                'absd': 'str',
                'geometrie': 'str',
                'geometrie_dec': 'str',
                'codegare': 'str',
                'codeoperationnel': 'str',
                'codereseau': 'str',
                'nomgarefr': 'str',
                'typegare': 'str',
                'publishid': 'str',
                'sivtypegare': 'str',
                'num_pk': 'str',
                'idville': 'int',
                'villes_ville': 'str',
                'etat': 'str'
            },
            'graphe_arc': {
                'id': 'int',
                'axe': 'str',
                'cumuld': 'float',
                'cumulf': 'float',
                'plod': 'str',
                'absd': 'float',
                'plof': 'str',
                'absf': 'float',
                'geometrie': 'str'
            },
            'ge_evenement': {
                'id': 'int',
                'date_debut': 'datetime',
                'date_fin': 'datetime',
                'col3': 'str',
                'col4': 'str',
                'date_creation': 'datetime',
                'type_id': 'int',
                'statut': 'str',
                'heure_debut': 'time',
                'heure_fin': 'time',
                'col10': 'str',
                'col11': 'str',
                'col12': 'bool',
                'col13': 'bool',
                'col14': 'bool',
                'col15': 'bool',
                'description': 'str'
            },
            'ref_types': {
                'id': 'int',
                'date_creation': 'datetime',
                'libelle': 'str',
                'niveau': 'int',
                'systeme_id': 'int',
                'actif': 'bool',
                'supprime': 'bool'
            },
            'ge_localisation': {
                'id': 'int',
                'axe': 'str',
                'pk_debut': 'float',
                'pk_fin': 'float',
                'voie': 'str',
                'section': 'str',
                'gare': 'str',
                'description': 'str',
                'col8': 'str', 'col9': 'str', 'col10': 'str', 'col11': 'str',
                'col12': 'str', 'col13': 'str', 'col14': 'str', 'col15': 'str',
                'col16': 'str', 'col17': 'str', 'col18': 'str', 'col19': 'str',
                'col20': 'str'
            },
            'ref_sous_types': {
                'id': 'int',
                'date_creation': 'datetime',
                'libelle': 'str',
                'type_id': 'int',
                'systeme_id': 'int',
                'actif': 'bool',
                'supprime': 'bool',
                'col7': 'str', 'col8': 'str', 'col9': 'str', 'col10': 'str',
                'col11': 'str', 'col12': 'str', 'col13': 'str', 'col14': 'str',
                'col15': 'str', 'col16': 'str', 'col17': 'str', 'col18': 'str',
                'col19': 'str', 'col20': 'str'
            }
        }
        
        total_imported = 0
        for csv_file, mapping in mappings.items():
            count = import_csv_file(cursor, csv_file, csv_file, mapping)
            total_imported += count
        
        # Valider les changements
        conn.commit()
        
        # Créer des index pour les performances
        print("\n🔧 Création des index...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_gares_axe ON gpr.gpd_gares_ref(axe);",
            "CREATE INDEX IF NOT EXISTS idx_gares_type ON gpr.gpd_gares_ref(typegare);",
            "CREATE INDEX IF NOT EXISTS idx_arcs_axe ON gpr.graphe_arc(axe);",
            "CREATE INDEX IF NOT EXISTS idx_evenements_date ON gpr.ge_evenement(date_debut);",
            "CREATE INDEX IF NOT EXISTS idx_evenements_statut ON gpr.ge_evenement(statut);",
            "CREATE INDEX IF NOT EXISTS idx_types_actif ON gpr.ref_types(actif);"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"⚠️  Erreur création index: {e}")
        
        conn.commit()
        print("✅ Index créés")
        
        # Afficher les statistiques finales
        print(f"\n📈 Résumé de l'import:")
        tables_stats = [
            ('gpr.gpd_gares_ref', 'Gares'),
            ('gpr.graphe_arc', 'Arcs/Sections'),
            ('gpr.ge_evenement', 'Événements'),
            ('gpr.ref_types', 'Types d\'incidents'),
            ('gpr.ge_localisation', 'Localisations'),
            ('gpr.ref_sous_types', 'Sous-types')
        ]
        
        for table, name in tables_stats:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"   - {name}: {count:,} enregistrements")
        
        print(f"\n🎉 Import terminé avec succès!")
        print(f"   Total: {total_imported:,} enregistrements importés")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'import: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Fonction principale"""
    print("🚂 ONCF GIS - Import des Vraies Données")
    print("=" * 50)
    
    if not os.path.exists('sql_data'):
        print("❌ Dossier 'sql_data' non trouvé!")
        print("Placez vos fichiers CSV dans le dossier sql_data/")
        return
    
    print("📁 Fichiers CSV détectés:")
    csv_files = [f for f in os.listdir('sql_data') if f.endswith('.csv') or not '.' in f]
    for f in csv_files:
        size = os.path.getsize(f'sql_data/{f}') / 1024
        print(f"   - {f} ({size:.1f} KB)")
    
    if not csv_files:
        print("⚠️  Aucun fichier CSV trouvé dans sql_data/")
        return
    
    print(f"\n🔄 Démarrage de l'import...")
    
    if import_all_data():
        print("\n✅ Import des vraies données terminé!")
        print("\nVous pouvez maintenant:")
        print("1. Lancer l'application: python app.py")
        print("2. Accéder aux incidents: http://localhost:5000/incidents")
        print("3. Voir les statistiques complètes sur le dashboard")
    else:
        print("\n❌ L'import a échoué")
        print("Vérifiez vos fichiers CSV et la configuration de la base de données")

if __name__ == "__main__":
    main()