#!/usr/bin/env python3
"""
Script d'import des données depuis PostgreSQL existant vers le schéma ONCF GIS
Les tables existent déjà et sont remplies dans la base oncf_ems_db
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def connect_to_database(db_name=None):
    """Établir une connexion à la base de données PostgreSQL"""
    try:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_ems_db')
        if db_name:
            # Remplacer le nom de la base dans l'URL
            parts = db_url.split('/')
            parts[-1] = db_name
            db_url = '/'.join(parts)
        
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def check_existing_tables():
    """Vérifier les tables existantes dans la base source"""
    conn = connect_to_database()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    try:
        # Lister toutes les tables avec leurs schémas
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
        
        print("📊 Tables existantes dans la base de données:")
        print("-" * 60)
        
        for schema, table, count in tables:
            print(f"   {schema}.{table} : {count:,} enregistrements")
        
        return tables
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des tables: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def analyze_table_structure(schema, table):
    """Analyser la structure d'une table"""
    conn = connect_to_database()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        
        columns = cursor.fetchall()
        return columns
        
    except Exception as e:
        print(f"❌ Erreur analyse structure {schema}.{table}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def create_target_schema():
    """Créer le schéma gpr dans la base de données cible"""
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Créer le schéma gpr
        cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr;")
        
        # Supprimer les tables existantes pour recommencer proprement
        tables_to_drop = [
            'gpr.ge_evenement',
            'gpr.gpd_gares_ref', 
            'gpr.graphe_arc',
            'gpr.ref_types',
            'gpr.ge_localisation',
            'gpr.ref_sous_types',
            'gpr.ref_systemes',
            'gpr.ref_sources',
            'gpr.ref_entites'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        
        conn.commit()
        print("✅ Schéma gpr créé et tables nettoyées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création schéma: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def copy_table_data(source_schema, source_table, target_schema, target_table, column_mapping=None):
    """Copier les données d'une table source vers une table cible"""
    conn = connect_to_database()
    if not conn:
        return 0
    
    cursor = conn.cursor()
    
    try:
        # Analyser la structure de la table source
        columns = analyze_table_structure(source_schema, source_table)
        if not columns:
            print(f"⚠️  Impossible d'analyser {source_schema}.{source_table}")
            return 0
        
        # Construire la requête CREATE TABLE
        create_columns = []
        for col_name, data_type, nullable, default in columns:
            col_def = f"{col_name} "
            
            # Mapper les types PostgreSQL
            if data_type in ['integer', 'bigint']:
                col_def += "INTEGER"
            elif data_type in ['numeric', 'decimal']:
                col_def += "NUMERIC"
            elif data_type in ['timestamp without time zone', 'timestamp with time zone']:
                col_def += "TIMESTAMP"
            elif data_type == 'time without time zone':
                col_def += "TIME"
            elif data_type == 'boolean':
                col_def += "BOOLEAN"
            elif data_type in ['character varying', 'text', 'character']:
                col_def += "TEXT"
            elif data_type == 'USER-DEFINED':  # Probablement geometry
                col_def += "TEXT"
            else:
                col_def += "TEXT"  # Par défaut
            
            # Gérer la clé primaire
            if col_name == 'id' and 'nextval' in str(default):
                col_def = f"{col_name} SERIAL PRIMARY KEY"
            elif nullable == 'NO' and col_name != 'id':
                col_def += " NOT NULL"
            
            create_columns.append(col_def)
        
        # Créer la table cible
        create_sql = f"""
            CREATE TABLE {target_schema}.{target_table} (
                {', '.join(create_columns)}
            );
        """
        
        cursor.execute(create_sql)
        print(f"✅ Table {target_schema}.{target_table} créée")
        
        # Copier les données
        column_names = [col[0] for col in columns]
        columns_str = ', '.join(column_names)
        
        # Requête de copie avec conversion des géométries
        copy_sql = f"""
            INSERT INTO {target_schema}.{target_table} ({columns_str})
            SELECT {columns_str}
            FROM {source_schema}.{source_table};
        """
        
        cursor.execute(copy_sql)
        rows_copied = cursor.rowcount
        
        conn.commit()
        print(f"✅ {rows_copied:,} lignes copiées dans {target_schema}.{target_table}")
        
        return rows_copied
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur copie {source_schema}.{source_table}: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def create_indexes():
    """Créer les index pour optimiser les performances"""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_gpr_gares_axe ON gpr.gpd_gares_ref(axe);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_gares_type ON gpr.gpd_gares_ref(typegare);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_gares_ville ON gpr.gpd_gares_ref(villes_ville);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_arcs_axe ON gpr.graphe_arc(axe);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_evenements_date ON gpr.ge_evenement(date_debut);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_evenements_statut ON gpr.ge_evenement(statut);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_evenements_type ON gpr.ge_evenement(type_id);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_types_actif ON gpr.ref_types(actif);",
        "CREATE INDEX IF NOT EXISTS idx_gpr_localisation_axe ON gpr.ge_localisation(axe);"
    ]
    
    try:
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Index créé: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"⚠️  Erreur index: {e}")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erreur création indexes: {e}")
    finally:
        cursor.close()
        conn.close()

def import_all_data():
    """Importer toutes les données depuis PostgreSQL"""
    print("🚂 ONCF GIS - Import depuis PostgreSQL")
    print("=" * 50)
    
    # Vérifier les tables existantes
    tables = check_existing_tables()
    if not tables:
        print("❌ Aucune table trouvée dans la base source")
        return False
    
    # Créer le schéma cible
    if not create_target_schema():
        return False
    
    print("\n📊 Import des données...")
    
    # Mapping des tables à copier
    table_mappings = [
        # (source_schema, source_table, target_schema, target_table)
        ('public', 'gpd_gares_ref', 'gpr', 'gpd_gares_ref'),
        ('public', 'graphe_arc', 'gpr', 'graphe_arc'),
        ('public', 'ge_evenement', 'gpr', 'ge_evenement'),
        ('public', 'ref_types', 'gpr', 'ref_types'),
        ('public', 'ge_localisation', 'gpr', 'ge_localisation'),
        ('public', 'ref_sous_types', 'gpr', 'ref_sous_types'),
        ('public', 'ref_systemes', 'gpr', 'ref_systemes'),
        ('public', 'ref_sources', 'gpr', 'ref_sources'),
        ('public', 'ref_entites', 'gpr', 'ref_entites'),
        # Essayer aussi le schéma gpr si les tables y sont déjà
        ('gpr', 'gpd_gares_ref', 'gpr', 'gpd_gares_ref'),
        ('gpr', 'graphe_arc', 'gpr', 'graphe_arc'),
        ('gpr', 'ge_evenement', 'gpr', 'ge_evenement'),
        ('gpr', 'ref_types', 'gpr', 'ref_types'),
        ('gpr', 'ge_localisation', 'gpr', 'ge_localisation'),
        ('gpr', 'ref_sous_types', 'gpr', 'ref_sous_types')
    ]
    
    total_copied = 0
    successful_copies = 0
    
    for source_schema, source_table, target_schema, target_table in table_mappings:
        # Vérifier si la table source existe
        table_exists = any(t[0] == source_schema and t[1] == source_table for t in tables)
        if not table_exists:
            continue
        
        print(f"\n📋 Copie de {source_schema}.{source_table} -> {target_schema}.{target_table}")
        rows = copy_table_data(source_schema, source_table, target_schema, target_table)
        
        if rows > 0:
            total_copied += rows
            successful_copies += 1
    
    if successful_copies == 0:
        print("\n⚠️  Aucune table copiée. Vérifiez que les tables existent dans la base source.")
        return False
    
    # Créer les index
    print("\n🔧 Création des index...")
    create_indexes()
    
    # Afficher le résumé
    print(f"\n📈 Résumé de l'import:")
    print(f"   - Tables copiées: {successful_copies}")
    print(f"   - Total d'enregistrements: {total_copied:,}")
    
    # Vérifier les données importées
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        
        verification_tables = [
            ('gpr.gpd_gares_ref', 'Gares'),
            ('gpr.graphe_arc', 'Arcs/Sections'),
            ('gpr.ge_evenement', 'Événements'),
            ('gpr.ref_types', 'Types d\'incidents'),
            ('gpr.ge_localisation', 'Localisations'),
            ('gpr.ref_sous_types', 'Sous-types')
        ]
        
        print(f"\n📊 Vérification des données importées:")
        for table, name in verification_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   ✅ {name}: {count:,} enregistrements")
            except:
                print(f"   ⚠️  {name}: Table non trouvée")
        
        cursor.close()
        conn.close()
    
    print(f"\n🎉 Import terminé avec succès!")
    print(f"   Application prête à utiliser vos données réelles!")
    
    return True

def main():
    """Fonction principale"""
    print("🔍 Vérification de la connexion à la base de données...")
    
    conn = connect_to_database()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        print("Vérifiez votre fichier .env et que PostgreSQL fonctionne")
        return
    
    print("✅ Connexion à la base de données réussie")
    conn.close()
    
    if import_all_data():
        print("\n🚀 Prochaines étapes:")
        print("1. Lancez l'application: python app.py")
        print("2. Accédez à: http://localhost:5000")
        print("3. Explorez vos données réelles dans l'interface!")
    else:
        print("\n❌ L'import a échoué")
        print("Vérifiez les logs ci-dessus pour plus de détails")

if __name__ == "__main__":
    main()