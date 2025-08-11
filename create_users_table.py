#!/usr/bin/env python3
"""
Script pour créer la table des utilisateurs et ajouter un administrateur par défaut
"""

import os
from dotenv import load_dotenv
from app import app, db, User

load_dotenv()

def create_users_table():
    """Créer la table des utilisateurs et ajouter un admin par défaut"""
    try:
        with app.app_context():
            print("🔧 Création de la table des utilisateurs")
            print("=" * 60)
            
            # Créer toutes les tables
            db.create_all()
            print("✅ Tables créées avec succès")
            
            # Vérifier si l'admin existe déjà
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("ℹ️  L'administrateur existe déjà")
                return True
            
            # Créer l'administrateur par défaut
            admin = User(
                username='admin',
                email='admin@oncf.ma',
                first_name='Administrateur',
                last_name='ONCF',
                role='admin'
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Administrateur créé avec succès")
            print("   👤 Nom d'utilisateur: admin")
            print("   🔑 Mot de passe: admin123")
            print("   📧 Email: admin@oncf.ma")
            
            # Créer quelques utilisateurs de test
            users_data = [
                {
                    'username': 'user1',
                    'email': 'user1@oncf.ma',
                    'first_name': 'Mohammed',
                    'last_name': 'Alaoui',
                    'password': 'user123'
                },
                {
                    'username': 'user2',
                    'email': 'user2@oncf.ma',
                    'first_name': 'Fatima',
                    'last_name': 'Benali',
                    'password': 'user123'
                },
                {
                    'username': 'user3',
                    'email': 'user3@oncf.ma',
                    'first_name': 'Ahmed',
                    'last_name': 'Tazi',
                    'password': 'user123'
                }
            ]
            
            for user_data in users_data:
                user = User.query.filter_by(username=user_data['username']).first()
                if not user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role='user'
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
            
            db.session.commit()
            print("✅ Utilisateurs de test créés")
            
            # Afficher le résumé
            total_users = User.query.count()
            print(f"\n📊 Résumé:")
            print(f"   👥 Total utilisateurs: {total_users}")
            print(f"   🔐 Comptes créés:")
            print(f"      - admin/admin123 (Administrateur)")
            print(f"      - user1/user123 (Mohammed Alaoui)")
            print(f"      - user2/user123 (Fatima Benali)")
            print(f"      - user3/user123 (Ahmed Tazi)")
            
            print(f"\n🎉 Configuration terminée!")
            print("Vous pouvez maintenant vous connecter avec l'un de ces comptes.")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_users_table() 