#!/usr/bin/env python3
"""
Script de démarrage rapide pour ONCF GIS
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Vérifier la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ est requis")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")

def check_dependencies():
    """Vérifier les dépendances"""
    required_packages = [
        'flask', 'psycopg2-binary', 'pandas', 'geopandas', 
        'folium', 'plotly', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def check_env_file():
    """Vérifier le fichier .env"""
    if not os.path.exists('.env'):
        print("⚠️  Fichier .env non trouvé")
        print("Création d'un fichier .env basique...")
        
        env_content = """# Configuration de base pour ONCF GIS
DATABASE_URL=postgresql://username:password@localhost:5432/oncf_db
SECRET_KEY=oncf-secret-key-2024-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Fichier .env créé")
        print("⚠️  IMPORTANT: Modifiez DATABASE_URL dans .env avec vos paramètres de base de données")
        return False
    
    print("✅ Fichier .env trouvé")
    return True

def check_database_connection():
    """Vérifier la connexion à la base de données"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import psycopg2
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.close()
        print("✅ Connexion à la base de données réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print("Vérifiez votre configuration dans le fichier .env")
        return False

def check_data_files():
    """Vérifier les fichiers de données"""
    data_files = ['sql_data/graphe_arc', 'sql_data/gpd_gares_ref']
    missing_files = []
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Fichiers de données manquants: {', '.join(missing_files)}")
        print("Assurez-vous que les fichiers CSV sont présents dans le dossier sql_data/")
        return False
    
    print("✅ Fichiers de données trouvés")
    return True

def import_data_if_needed():
    """Importer les données si nécessaire"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import psycopg2
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Vérifier si les tables contiennent des données
        cursor.execute("SELECT COUNT(*) FROM gpr.gpd_gares_ref;")
        gares_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gpr.graphe_arc;")
        arcs_count = cursor.fetchone()[0]
        
        conn.close()
        
        if gares_count == 0 or arcs_count == 0:
            print("⚠️  Base de données vide, importation des données...")
            subprocess.run([sys.executable, 'import_data.py'], check=True)
            print("✅ Données importées avec succès")
        else:
            print(f"✅ Base de données contient {gares_count} gares et {arcs_count} arcs")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des données: {e}")
        return False
    
    return True

def start_application():
    """Démarrer l'application"""
    print("\n🚀 Démarrage de l'application ONCF GIS...")
    print("=" * 50)
    
    try:
        # Vérifications préliminaires
        print("🔍 Vérifications préliminaires...")
        check_python_version()
        
        if not check_dependencies():
            return False
        
        if not check_env_file():
            print("⚠️  Veuillez configurer le fichier .env avant de continuer")
            return False
        
        if not check_data_files():
            print("⚠️  Veuillez placer les fichiers de données dans sql_data/")
            return False
        
        # Vérification de la base de données
        print("\n🗄️  Vérification de la base de données...")
        if not check_database_connection():
            return False
        
        if not import_data_if_needed():
            return False
        
        # Démarrage de l'application
        print("\n🌐 Démarrage du serveur web...")
        print("L'application sera accessible à: http://localhost:5000")
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        print("=" * 50)
        
        # Lancer l'application Flask
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\n\n👋 Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

def show_help():
    """Afficher l'aide"""
    print("""
🚂 ONCF GIS - Script de Démarrage Rapide

Usage:
  python start.py          # Démarrer l'application
  python start.py --help   # Afficher cette aide

Prérequis:
  - Python 3.8+
  - PostgreSQL avec PostGIS
  - Fichiers de données CSV dans sql_data/

Configuration:
  1. Copiez env.example vers .env
  2. Modifiez DATABASE_URL dans .env
  3. Lancez: python start.py

Pour plus d'informations, consultez README.md
""")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return
    
    print("🚂 ONCF GIS - Système d'Information Géographique")
    print("Script de démarrage rapide")
    print("=" * 50)
    
    success = start_application()
    
    if not success:
        print("\n❌ Le démarrage a échoué")
        print("Consultez les messages d'erreur ci-dessus")
        print("Pour de l'aide: python start.py --help")
        sys.exit(1)

if __name__ == "__main__":
    main() 