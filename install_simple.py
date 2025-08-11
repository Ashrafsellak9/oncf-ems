#!/usr/bin/env python3
"""
Script d'installation simplifié pour ONCF GIS
Compatible avec Python 3.13
"""

import subprocess
import sys
import os

def install_packages():
    """Installer les packages essentiels un par un"""
    essential_packages = [
        'flask>=3.0.0',
        'flask-sqlalchemy>=3.1.0',
        'psycopg2-binary>=2.9.0',
        'python-dotenv>=1.0.0',
        'werkzeug>=3.0.0',
        'gunicorn>=21.0.0'
    ]
    
    print("🔧 Installation des packages essentiels...")
    
    for package in essential_packages:
        print(f"📦 Installation de {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {package}: {e}")
            return False
    
    # Packages optionnels (pour les fonctionnalités avancées)
    optional_packages = [
        'plotly>=5.18.0',
        'folium>=0.15.0',
    ]
    
    print("\n🔧 Installation des packages optionnels...")
    
    for package in optional_packages:
        print(f"📦 Installation de {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur lors de l'installation de {package} (optionnel): {e}")
    
    return True

def create_env_file():
    """Créer le fichier .env s'il n'existe pas"""
    if not os.path.exists('.env'):
        print("📝 Création du fichier .env...")
        env_content = """# Configuration ONCF GIS
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/oncf_db
SECRET_KEY=oncf-secret-key-2024-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Fichier .env créé")
    else:
        print("✅ Fichier .env déjà présent")

def main():
    """Fonction principale"""
    print("🚂 ONCF GIS - Installation Simplifiée")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print("=" * 50)
    
    # Vérifier la version de Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ est requis")
        sys.exit(1)
    
    # Installer les packages
    if not install_packages():
        print("❌ L'installation a échoué")
        sys.exit(1)
    
    # Créer le fichier .env
    create_env_file()
    
    print("\n🎉 Installation terminée avec succès!")
    print("\nÉtapes suivantes:")
    print("1. Configurez votre base de données PostgreSQL")
    print("2. Modifiez DATABASE_URL dans le fichier .env")
    print("3. Placez vos fichiers CSV dans le dossier sql_data/")
    print("4. Lancez: python app.py")
    print("\nPour une installation complète avec pandas/geopandas:")
    print("- Utilisez Python 3.11 ou antérieur")
    print("- Ou attendez la compatibilité pandas avec Python 3.13")

if __name__ == "__main__":
    main()