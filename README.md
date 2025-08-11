# 🚂 ONCF GIS - Système d'Information Géographique

Une application web moderne et professionnelle pour la gestion et visualisation des données ferroviaires de l'Office National des Chemins de Fer (ONCF) du Maroc.

## ✨ Fonctionnalités

### 🗺️ Cartographie Interactive
- **Carte interactive** avec Leaflet.js
- **Visualisation des gares** et voies ferroviaires
- **Filtres avancés** par axe, type et région
- **Popups informatifs** pour chaque élément
- **Légende interactive** et contrôles de couches

### 📊 Dashboard Analytique
- **Statistiques en temps réel** du réseau
- **Graphiques interactifs** avec Chart.js
- **Métriques avancées** (densité, couverture, efficacité)
- **Tableaux de bord** personnalisables
- **Actualisation automatique** des données

### 🏢 Gestion des Gares
- **Tableau interactif** avec tri et pagination
- **Recherche avancée** et filtres multiples
- **CRUD complet** (Création, Lecture, Mise à jour, Suppression)
- **Export CSV** des données
- **Modales détaillées** pour chaque gare

### 📈 Statistiques Avancées
- **Graphiques multiples** (camembert, barres, lignes)
- **Analyse temporelle** de l'évolution du réseau
- **Répartition géographique** des infrastructures
- **Métriques de performance** du réseau

## 🛠️ Technologies Utilisées

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM pour la base de données
- **PostgreSQL** - Base de données principale
- **GeoPandas** - Traitement des données géospatiales

### Frontend
- **Bootstrap 5** - Framework CSS moderne
- **Leaflet.js** - Cartographie interactive
- **Chart.js** - Graphiques et visualisations
- **Font Awesome** - Icônes professionnelles
- **Vanilla JavaScript** - Interactivité

### Base de Données
- **PostgreSQL** avec extension PostGIS
- **Schéma GPR** pour les données géospatiales
- **Tables principales** : `graphe_arc` et `gpd_gares_ref`

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- PostGIS 3.0+

### 1. Cloner le Repository
```bash
git clone https://github.com/votre-username/oncf-gis.git
cd oncf-gis
```

### 2. Créer un Environnement Virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la Base de Données

#### Créer la Base de Données
```sql
CREATE DATABASE oncf_db;
CREATE EXTENSION postgis;
CREATE SCHEMA gpr;
```

#### Importer les Données
```bash
# Importer les données CSV depuis le dossier sql_data
psql -d oncf_db -c "\copy gpr.graphe_arc FROM 'sql_data/graphe_arc.csv' CSV HEADER;"
psql -d oncf_db -c "\copy gpr.gpd_gares_ref FROM 'sql_data/gpd_gares_ref.csv' CSV HEADER;"
```

### 5. Configuration de l'Environnement
Créer un fichier `.env` à la racine du projet :
```env
DATABASE_URL=postgresql://username:password@localhost:5432/oncf_db
SECRET_KEY=votre-cle-secrete-ici
FLASK_ENV=development
```

### 6. Lancer l'Application
```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

## 📁 Structure du Projet

```
oncf_gis/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
├── .env                  # Variables d'environnement
├── sql_data/             # Données CSV exportées
│   ├── graphe_arc.csv
│   ├── gpd_gares_ref.csv
│   └── ...
├── static/               # Fichiers statiques
│   ├── css/
│   │   └── style.css     # Styles personnalisés
│   ├── js/
│   │   ├── main.js       # JavaScript principal
│   │   ├── carte.js      # Logique de la carte
│   │   └── gares.js      # Gestion des gares
│   └── images/
└── templates/            # Templates HTML
    ├── base.html         # Template de base
    ├── index.html        # Page d'accueil
    ├── dashboard.html    # Dashboard
    ├── carte.html        # Carte interactive
    ├── statistiques.html # Statistiques
    └── gares.html        # Gestion des gares
```

## 🎯 Utilisation

### Page d'Accueil
- **Vue d'ensemble** du système
- **Statistiques rapides** du réseau
- **Accès direct** aux principales fonctionnalités

### Dashboard
- **Métriques en temps réel** du réseau ferroviaire
- **Graphiques interactifs** de répartition
- **Tableau des gares récentes**
- **Alertes système** et activité récente

### Carte Interactive
- **Navigation** dans le réseau ferroviaire
- **Filtres par couches** (gares, voies, axes)
- **Informations détaillées** au clic
- **Légende interactive** et contrôles

### Gestion des Gares
- **Recherche avancée** par nom, code, ville
- **Filtres multiples** (axe, type, état)
- **Tri et pagination** des résultats
- **Ajout/modification** des gares
- **Export des données** en CSV

### Statistiques
- **Graphiques détaillés** de répartition
- **Analyse temporelle** de l'évolution
- **Métriques avancées** de performance
- **Tableaux de données** avec pourcentages

## 🔧 Configuration Avancée

### Personnalisation des Styles
Modifiez `static/css/style.css` pour adapter l'apparence :
```css
:root {
    --primary-color: #0d6efd;
    --oncf-blue: #1e3a8a;
    --oncf-orange: #ea580c;
}
```

### Ajout de Nouvelles Fonctionnalités
1. **Nouvelles routes** dans `app.py`
2. **Templates HTML** dans `templates/`
3. **JavaScript** dans `static/js/`
4. **Styles CSS** dans `static/css/`

### Base de Données
Pour ajouter de nouvelles tables :
```python
class NouvelleTable(db.Model):
    __tablename__ = 'nouvelle_table'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    # Autres colonnes...
```

## 🚀 Déploiement

### Production avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (Optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 API Endpoints

### Gares
- `GET /api/gares` - Liste des gares
- `GET /api/gares/{id}` - Détails d'une gare
- `POST /api/gares` - Créer une gare
- `PUT /api/gares/{id}` - Modifier une gare
- `DELETE /api/gares/{id}` - Supprimer une gare

### Arcs (Voies)
- `GET /api/arcs` - Liste des sections de voie
- `GET /api/arcs/{id}` - Détails d'un arc

### Statistiques
- `GET /api/statistiques` - Statistiques globales
- `GET /api/statistiques/gares` - Statistiques des gares
- `GET /api/statistiques/arcs` - Statistiques des voies

## 🤝 Contribution

1. **Fork** le projet
2. **Créer** une branche pour votre fonctionnalité
3. **Commiter** vos changements
4. **Pousser** vers la branche
5. **Ouvrir** une Pull Request

## 📝 Licence

Ce projet est développé pour l'Office National des Chemins de Fer (ONCF) du Maroc.

## 👥 Équipe de Développement

- **Développeur Principal** : [Votre Nom]
- **Technologies** : Flask, PostgreSQL, Leaflet.js, Bootstrap
- **Année** : 2024

## 📞 Support

Pour toute question ou support :
- **Email** : support@oncf.ma
- **Documentation** : [Lien vers la documentation]
- **Issues** : [Lien vers GitHub Issues]

---

**ONCF GIS** - Système d'Information Géographique Professionnel pour le Réseau Ferroviaire Marocain 🚂🇲🇦 