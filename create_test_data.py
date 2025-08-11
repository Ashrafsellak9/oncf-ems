#!/usr/bin/env python3
"""
Créer des données de test pour ONCF GIS sans pandas
"""

import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def create_test_data():
    """Créer des données de test dans la base de données"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Créer le schéma
        cursor.execute("CREATE SCHEMA IF NOT EXISTS gpr;")
        
        # Créer la table des gares
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
        
        # Créer la table des arcs
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
        
        # Vider les tables existantes
        cursor.execute("TRUNCATE TABLE gpr.gpd_gares_ref RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE gpr.graphe_arc RESTART IDENTITY CASCADE;")
        
        # Insérer des données de test pour les gares
        gares_test = [
            ('CASABLANCA-RABAT', 'CASA', '0', 'POINT(-7.6167 33.5731)', 'POINT(-7.6167 33.5731)', 'CASA', 'CASA01', 'ONCF', 'Casablanca Voyageurs', 'PRINCIPALE', 'PUB001', 'PRINCIPALE', 'PK0', 1, 'Casablanca', 'ACTIVE'),
            ('CASABLANCA-RABAT', 'RABAT', '87', 'POINT(-6.8498 34.0209)', 'POINT(-6.8498 34.0209)', 'RABAT', 'RAB01', 'ONCF', 'Rabat Ville', 'PRINCIPALE', 'PUB002', 'PRINCIPALE', 'PK87', 2, 'Rabat', 'ACTIVE'),
            ('CASABLANCA-RABAT', 'SALE', '90', 'POINT(-6.7989 34.0531)', 'POINT(-6.7989 34.0531)', 'SALE', 'SAL01', 'ONCF', 'Salé', 'SECONDAIRE', 'PUB003', 'SECONDAIRE', 'PK90', 3, 'Salé', 'ACTIVE'),
            ('FES-OUJDA', 'FES', '0', 'POINT(-4.9998 34.0331)', 'POINT(-4.9998 34.0331)', 'FES', 'FES01', 'ONCF', 'Fès', 'PRINCIPALE', 'PUB004', 'PRINCIPALE', 'PK0', 4, 'Fès', 'ACTIVE'),
            ('FES-OUJDA', 'OUJDA', '320', 'POINT(-1.9077 34.6814)', 'POINT(-1.9077 34.6814)', 'OUJDA', 'OUJ01', 'ONCF', 'Oujda', 'PRINCIPALE', 'PUB005', 'PRINCIPALE', 'PK320', 5, 'Oujda', 'ACTIVE'),
            ('CASABLANCA-MARRAKECH', 'MARR', '240', 'POINT(-7.9811 31.6295)', 'POINT(-7.9811 31.6295)', 'MARR', 'MAR01', 'ONCF', 'Marrakech', 'PRINCIPALE', 'PUB006', 'PRINCIPALE', 'PK240', 6, 'Marrakech', 'ACTIVE'),
            ('TANGER-FES', 'TANG', '0', 'POINT(-5.8008 35.7595)', 'POINT(-5.8008 35.7595)', 'TANG', 'TAN01', 'ONCF', 'Tanger Ville', 'PRINCIPALE', 'PUB007', 'PRINCIPALE', 'PK0', 7, 'Tanger', 'ACTIVE'),
            ('CASABLANCA-RABAT', 'KENITRA', '40', 'POINT(-6.5802 34.2610)', 'POINT(-6.5802 34.2610)', 'KEN', 'KEN01', 'ONCF', 'Kénitra', 'SECONDAIRE', 'PUB008', 'SECONDAIRE', 'PK40', 8, 'Kénitra', 'ACTIVE'),
            ('CASABLANCA-MARRAKECH', 'SETTAT', '60', 'POINT(-7.6218 33.0013)', 'POINT(-7.6218 33.0013)', 'SET', 'SET01', 'ONCF', 'Settat', 'SECONDAIRE', 'PUB009', 'SECONDAIRE', 'PK60', 9, 'Settat', 'ACTIVE'),
            ('FES-OUJDA', 'TAZA', '120', 'POINT(-4.0103 34.2133)', 'POINT(-4.0103 34.2133)', 'TAZA', 'TAZ01', 'ONCF', 'Taza', 'SECONDAIRE', 'PUB010', 'SECONDAIRE', 'PK120', 10, 'Taza', 'ACTIVE')
        ]
        
        for gare in gares_test:
            cursor.execute("""
                INSERT INTO gpr.gpd_gares_ref 
                (axe, plod, absd, geometrie, geometrie_dec, codegare, codeoperationnel, 
                 codereseau, nomgarefr, typegare, publishid, sivtypegare, num_pk, 
                 idville, villes_ville, etat)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, gare)
        
        # Insérer des données de test pour les arcs
        arcs_test = [
            ('CASABLANCA-RABAT', 0, 40, 'CASA', 0, 'KENITRA', 40, 'LINESTRING(-7.6167 33.5731, -6.5802 34.2610)'),
            ('CASABLANCA-RABAT', 40, 87, 'KENITRA', 40, 'RABAT', 87, 'LINESTRING(-6.5802 34.2610, -6.8498 34.0209)'),
            ('CASABLANCA-RABAT', 87, 90, 'RABAT', 87, 'SALE', 90, 'LINESTRING(-6.8498 34.0209, -6.7989 34.0531)'),
            ('CASABLANCA-MARRAKECH', 0, 60, 'CASA', 0, 'SETTAT', 60, 'LINESTRING(-7.6167 33.5731, -7.6218 33.0013)'),
            ('CASABLANCA-MARRAKECH', 60, 240, 'SETTAT', 60, 'MARR', 240, 'LINESTRING(-7.6218 33.0013, -7.9811 31.6295)'),
            ('FES-OUJDA', 0, 120, 'FES', 0, 'TAZA', 120, 'LINESTRING(-4.9998 34.0331, -4.0103 34.2133)'),
            ('FES-OUJDA', 120, 320, 'TAZA', 120, 'OUJDA', 320, 'LINESTRING(-4.0103 34.2133, -1.9077 34.6814)'),
            ('TANGER-FES', 0, 200, 'TANG', 0, 'FES', 200, 'LINESTRING(-5.8008 35.7595, -4.9998 34.0331)')
        ]
        
        for arc in arcs_test:
            cursor.execute("""
                INSERT INTO gpr.graphe_arc 
                (axe, cumuld, cumulf, plod, absd, plof, absf, geometrie)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, arc)
        
        # Valider les changements
        conn.commit()
        
        # Vérifier les données
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        gares_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        arcs_count = cursor.fetchone()[0]
        
        print(f"✅ Données de test créées avec succès:")
        print(f"   - {gares_count} gares")
        print(f"   - {arcs_count} sections de voie")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données de test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚂 ONCF GIS - Création de Données de Test")
    print("=" * 50)
    
    if create_test_data():
        print("\n🎉 Données de test créées avec succès!")
        print("\nVous pouvez maintenant lancer l'application avec:")
        print("   python app.py")
    else:
        print("\n❌ Échec de la création des données de test")
        print("Vérifiez votre configuration de base de données dans .env")

if __name__ == "__main__":
    main()