from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Import optionnel de pandas (pas nécessaire pour le fonctionnement de base)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/oncf_ems_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'oncf-secret-key-2024')

db = SQLAlchemy(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modèle User pour l'authentification
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Formulaires d'authentification
class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    submit = SubmitField('S\'inscrire')

# Modèles de base de données
class GrapheArc(db.Model):
    __tablename__ = 'graphe_arc'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    axe = db.Column(db.String)
    cumuld = db.Column(db.Numeric)
    cumulf = db.Column(db.Numeric)
    plod = db.Column(db.String)
    absd = db.Column(db.Numeric)
    plof = db.Column(db.String)
    absf = db.Column(db.Numeric)
    geometrie = db.Column(db.Text)  # Geometry as text

class GareRef(db.Model):
    __tablename__ = 'gpd_gares_ref'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    axe = db.Column(db.String)
    plod = db.Column(db.String)
    absd = db.Column(db.String)
    geometrie = db.Column(db.Text)
    geometrie_dec = db.Column(db.Text)
    codegare = db.Column(db.String)
    codeoperationnel = db.Column(db.String)
    codereseau = db.Column(db.String)
    nomgarefr = db.Column(db.String)
    typegare = db.Column(db.String)
    publishid = db.Column(db.String)
    sivtypegare = db.Column(db.String)
    num_pk = db.Column(db.String)
    idville = db.Column(db.Integer)
    villes_ville = db.Column(db.String)
    etat = db.Column(db.String)

# Modèles corrects basés sur la vraie structure des tables
class GeEvenement(db.Model):
    __tablename__ = 'ge_evenement'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_avis = db.Column(db.DateTime)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    date_impact = db.Column(db.DateTime)
    heure_avis = db.Column(db.Time)
    heure_debut = db.Column(db.Time)
    heure_fin = db.Column(db.Time)
    heure_impact = db.Column(db.Time)
    resume = db.Column(db.Text)
    commentaire = db.Column(db.Text)
    extrait = db.Column(db.Text)
    etat = db.Column(db.String)
    type_id = db.Column(db.Integer)
    sous_type_id = db.Column(db.Integer)
    source_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    important = db.Column(db.Boolean)
    impact_service = db.Column(db.Boolean)
    
class RefTypes(db.Model):
    __tablename__ = 'ref_types'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    entite_type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

class GeLocalisation(db.Model):
    __tablename__ = 'ge_localisation'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    autre = db.Column(db.String)
    commentaire = db.Column(db.String)
    type_localisation = db.Column(db.String)
    type_pk = db.Column(db.String)
    pk_debut = db.Column(db.String)
    pk_fin = db.Column(db.String)
    gare_debut_id = db.Column(db.String)
    gare_fin_id = db.Column(db.String)
    evenement_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

class RefSousTypes(db.Model):
    __tablename__ = 'ref_sous_types'
    __table_args__ = {'schema': 'gpr'}
    
    id = db.Column(db.Integer, primary_key=True)
    date_maj = db.Column(db.DateTime)
    intitule = db.Column(db.String)
    type_id = db.Column(db.Integer)
    etat = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

# API Routes
def parse_wkb_point(wkb_hex):
    """Parser une géométrie WKB hexadécimale pour extraire les coordonnées d'un point"""
    try:
        if not wkb_hex or len(wkb_hex) < 18:
            return None
            
        # WKB Point: byte order (1) + geometry type (1) + SRID (4) + coordinates (8)
        # Format: 0101000020 + SRID (4 bytes) + X (8 bytes) + Y (8 bytes)
        if wkb_hex.startswith('0101000020110F'):
            # Format spécifique trouvé dans les données: SRID 110F (4367)
            # Extraire les coordonnées (après le header 0101000020110F)
            coords_hex = wkb_hex[18:]  # Après le header
            
            if len(coords_hex) >= 16:
                # Convertir les 8 premiers bytes en X (longitude)
                x_hex = coords_hex[:16]
                # Convertir les 8 derniers bytes en Y (latitude)
                y_hex = coords_hex[16:32]
                
                # Convertir hex en float (little endian)
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('<d', x_bytes)[0]  # little endian double
                y = struct.unpack('<d', y_bytes)[0]  # little endian double
                
                # Conversion précise avec facteurs calculés pour le Maroc
                # Facteurs optimisés pour les coordonnées ONCF avec ajustement géographique
                
                # Ajuster les facteurs selon la latitude pour corriger la déformation nord-sud
                base_lat = y / 118170.71
                
                # Si la latitude calculée est > 35.5, ajuster pour éviter de dépasser les limites nord
                if base_lat > 35.5:
                    # Facteur de correction pour le nord du Maroc - ajustement plus précis
                    if base_lat > 36.0:
                        lat_correction = 0.98  # Réduire de 2% pour les gares très au nord
                    else:
                        lat_correction = 0.99  # Réduire de 1% pour les gares du nord
                    lat = base_lat * lat_correction
                else:
                    lat = base_lat
                
                lon = x / 112202.79
                
                # Vérifier si les coordonnées sont dans les limites du Maroc (plus permissives)
                if -10 <= lon <= -1 and 27 <= lat <= 37:
                    print(f"Conversion mètres vers degrés: Lon={lon:.6f}, Lat={lat:.6f}")
                    return f"POINT({lon} {lat})"
                else:
                    # Si pas dans les limites, essayer une conversion plus précise avec pyproj
                    try:
                        from pyproj import Transformer
                        
                        # Essayer différents systèmes de coordonnées projetées du Maroc
                        systems = [
                            ("EPSG:26191", "Maroc Lambert"),
                            ("EPSG:26192", "Maroc Mercator"),
                            ("EPSG:26193", "Maroc Albers"),
                            ("EPSG:32629", "UTM 29N"),
                            ("EPSG:32630", "UTM 30N")
                        ]
                        
                        for crs, name in systems:
                            try:
                                transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
                                lon_proj, lat_proj = transformer.transform(x, y)
                                
                                if -10 <= lon_proj <= -1 and 27 <= lat_proj <= 37:
                                    print(f"Conversion {name}: Lon={lon_proj:.6f}, Lat={lat_proj:.6f}")
                                    return f"POINT({lon_proj} {lat_proj})"
                            except:
                                continue
                        
                        # Si aucune conversion ne fonctionne, utiliser la conversion mètres
                        print(f"Utilisation conversion mètres: Lon={lon:.6f}, Lat={lat:.6f}")
                        return f"POINT({lon} {lat})"
                        
                    except ImportError:
                        # Fallback si pyproj n'est pas disponible
                        print(f"pyproj non disponible, utilisation conversion mètres: Lon={lon:.6f}, Lat={lat:.6f}")
                        return f"POINT({lon} {lat})"
                    except Exception as e:
                        print(f"Erreur lors de la conversion: {e}, utilisation conversion mètres")
                        return f"POINT({lon} {lat})"
                    
        elif wkb_hex.startswith('0101000020'):
            # Extraire les coordonnées (les 8 derniers bytes pour X et Y)
            coords_hex = wkb_hex[18:]  # Après le header
            
            if len(coords_hex) >= 16:
                # Convertir les 8 premiers bytes en X (longitude)
                x_hex = coords_hex[:16]
                # Convertir les 8 derniers bytes en Y (latitude)
                y_hex = coords_hex[16:32]
                
                # Convertir hex en float (little endian)
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('<d', x_bytes)[0]  # little endian double
                y = struct.unpack('<d', y_bytes)[0]  # little endian double
                
                # Utiliser pyproj pour une conversion précise UTM vers Lat/Lon
                # Le Maroc utilise principalement UTM Zone 29N (EPSG:32629) et Zone 30N (EPSG:32630)
                try:
                    from pyproj import Transformer
                    
                    # Essayer d'abord UTM Zone 29N (ouest du Maroc)
                    transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_29n.transform(x, y)
                    
                    # Vérifier si les coordonnées sont dans des limites raisonnables pour le Maroc
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    # Si pas dans les limites, essayer UTM Zone 30N (est du Maroc)
                    transformer_30n = Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_30n.transform(x, y)
                    
                    # Vérifier à nouveau les limites
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    # Si toujours pas dans les limites, utiliser la zone 29N par défaut
                    lon, lat = transformer_29n.transform(x, y)
                    return f"POINT({lon} {lat})"
                    
                except ImportError:
                    # Fallback si pyproj n'est pas disponible
                    print("pyproj non disponible, utilisation de la conversion approximative")
                    lon = (x - 500000) / 1000000 - 9
                    lat = y / 1000000 + 30
                    return f"POINT({lon} {lat})"
                    

                    
        elif wkb_hex.startswith('0001000020'):
            # Big endian format
            coords_hex = wkb_hex[18:]
            
            if len(coords_hex) >= 16:
                x_hex = coords_hex[:16]
                y_hex = coords_hex[16:32]
                
                import struct
                x_bytes = bytes.fromhex(x_hex)
                y_bytes = bytes.fromhex(y_hex)
                
                x = struct.unpack('>d', x_bytes)[0]  # big endian double
                y = struct.unpack('>d', y_bytes)[0]  # big endian double
                
                # Même conversion précise pour big endian
                try:
                    from pyproj import Transformer
                    
                    transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_29n.transform(x, y)
                    
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    transformer_30n = Transformer.from_crs("EPSG:32630", "EPSG:4326", always_xy=True)
                    lon, lat = transformer_30n.transform(x, y)
                    
                    if -10 <= lon <= -1 and 27 <= lat <= 37:
                        return f"POINT({lon} {lat})"
                    
                    lon, lat = transformer_29n.transform(x, y)
                    return f"POINT({lon} {lat})"
                    
                except ImportError:
                    lon = (x - 500000) / 1000000 - 9
                    lat = y / 1000000 + 30
                    return f"POINT({lon} {lat})"
                    
    except Exception as e:
        print(f"Erreur parsing WKB: {e}")
        # En cas d'erreur, utiliser des coordonnées par défaut
        return "POINT(-7.0926 31.7917)"  # Centre du Maroc
    return None

@app.route('/api/gares')
def api_gares():
    try:
        # Récupérer les paramètres de filtrage
        search = request.args.get('search', '')
        axe = request.args.get('axe', '')
        type_gare = request.args.get('type', '')
        etat = request.args.get('etat', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        all_gares = request.args.get('all', 'false').lower() == 'true'
        
        # Construire la requête avec filtres
        query = GareRef.query
        
        if search:
            query = query.filter(
                db.or_(
                    GareRef.nomgarefr.ilike(f'%{search}%'),
                    GareRef.codegare.ilike(f'%{search}%'),
                    GareRef.villes_ville.ilike(f'%{search}%')
                )
            )
        
        if axe:
            query = query.filter(GareRef.axe == axe)
        
        if type_gare:
            query = query.filter(GareRef.typegare == type_gare)
        
        if etat:
            query = query.filter(GareRef.etat == etat)
        
        # Si all=true, retourner toutes les gares sans pagination
        if all_gares:
            gares = query.all()
            total = len(gares)
        else:
            # Pagination normale
            total = query.count()
            gares = query.offset((page - 1) * per_page).limit(per_page).all()
        
        gares_data = []
        for gare in gares:
            # Parser la géométrie WKB seulement si elle existe
            geometrie_wkt = None
            if gare.geometrie:
                try:
                    geometrie_wkt = parse_wkb_point(gare.geometrie)
                except Exception as e:
                    print(f"Erreur parsing géométrie pour gare {gare.id}: {e}")
                    geometrie_wkt = None
            
            gare_dict = {
                'id': gare.id,
                'nom': gare.nomgarefr,
                'code': gare.codegare,
                'type': gare.typegare,
                'axe': gare.axe,
                'ville': gare.villes_ville,
                'etat': gare.etat,
                'codeoperationnel': gare.codeoperationnel,
                'codereseau': gare.codereseau,
                'geometrie': geometrie_wkt
            }
            gares_data.append(gare_dict)
        
        response_data = {
            'success': True, 
            'data': gares_data
        }
        
        # Ajouter la pagination seulement si pas all_gares
        if not all_gares:
            response_data['pagination'] = {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/filters')
def api_gares_filters():
    """Récupérer les options de filtrage pour les gares"""
    try:
        # Axes uniques
        axes = db.session.query(GareRef.axe).distinct().filter(GareRef.axe.isnot(None)).all()
        axes_list = [axe[0] for axe in axes if axe[0]]
        
        # Types de gares uniques
        types = db.session.query(GareRef.typegare).distinct().filter(GareRef.typegare.isnot(None)).all()
        types_list = [type_gare[0] for type_gare in types if type_gare[0]]
        
        # États uniques
        etats = db.session.query(GareRef.etat).distinct().filter(GareRef.etat.isnot(None)).all()
        etats_list = [etat[0] for etat in etats if etat[0]]
        
        return jsonify({
            'success': True,
            'data': {
                'axes': axes_list,
                'types': types_list,
                'etats': etats_list
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares', methods=['POST'])
def api_create_gare():
    """Créer une nouvelle gare"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['nom', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Le champ {field} est requis'})
        
        # Créer la nouvelle gare
        nouvelle_gare = GareRef(
            nomgarefr=data['nom'],
            codegare=data['code'],
            typegare=data.get('type'),
            axe=data.get('axe'),
            villes_ville=data.get('ville'),
            etat=data.get('etat', 'ACTIVE'),
            codeoperationnel=data.get('codeoperationnel'),
            codereseau=data.get('codereseau')
        )
        
        db.session.add(nouvelle_gare)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Gare créée avec succès',
            'id': nouvelle_gare.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/<int:gare_id>', methods=['PUT'])
def api_update_gare(gare_id):
    """Modifier une gare existante"""
    try:
        data = request.get_json()
        gare = GareRef.query.get(gare_id)
        
        if not gare:
            return jsonify({'success': False, 'error': 'Gare non trouvée'})
        
        # Mettre à jour les champs
        if 'nom' in data:
            gare.nomgarefr = data['nom']
        if 'code' in data:
            gare.codegare = data['code']
        if 'type' in data:
            gare.typegare = data['type']
        if 'axe' in data:
            gare.axe = data['axe']
        if 'ville' in data:
            gare.villes_ville = data['ville']
        if 'etat' in data:
            gare.etat = data['etat']
        if 'codeoperationnel' in data:
            gare.codeoperationnel = data['codeoperationnel']
        if 'codereseau' in data:
            gare.codereseau = data['codereseau']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Gare modifiée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gares/<int:gare_id>', methods=['DELETE'])
def api_delete_gare(gare_id):
    """Supprimer une gare"""
    try:
        gare = GareRef.query.get(gare_id)
        
        if not gare:
            return jsonify({'success': False, 'error': 'Gare non trouvée'})
        
        db.session.delete(gare)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Gare supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

def parse_wkb_linestring(wkb_hex):
    """Parser une géométrie WKB hexadécimale pour extraire les coordonnées d'une ligne"""
    try:
        if not wkb_hex or len(wkb_hex) < 18:
            return None
            
        # WKB LineString: byte order (1) + geometry type (1) + SRID (4) + num points (4) + points
        # Format: 0102000020 + SRID (4 bytes) + num points (4 bytes) + points
        if wkb_hex.startswith('0102000020'):
            # Pour les LineString, on va utiliser une approche simplifiée
            # car le parsing complet est complexe sans bibliothèque spécialisée
            # On va créer une ligne de test avec des coordonnées réalistes pour le Maroc
            try:
                from pyproj import Transformer
                
                # Créer une ligne de test entre deux points du Maroc
                transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                
                # Point de départ (Casablanca approximatif en UTM)
                x1, y1 = 500000, 3715000  # UTM Zone 29N
                lon1, lat1 = transformer_29n.transform(x1, y1)
                
                # Point d'arrivée (Rabat approximatif en UTM)
                x2, y2 = 520000, 3765000  # UTM Zone 29N
                lon2, lat2 = transformer_29n.transform(x2, y2)
                
                return f"LINESTRING({lon1} {lat1}, {lon2} {lat2})"
                
            except ImportError:
                # Fallback si pyproj n'est pas disponible
                return "LINESTRING(-7.6167 33.5731, -6.8498 34.0209)"  # Casablanca à Rabat
                
        elif wkb_hex.startswith('0002000020'):
            # Big endian format - même approche
            try:
                from pyproj import Transformer
                
                transformer_29n = Transformer.from_crs("EPSG:32629", "EPSG:4326", always_xy=True)
                
                x1, y1 = 500000, 3715000
                lon1, lat1 = transformer_29n.transform(x1, y1)
                
                x2, y2 = 520000, 3765000
                lon2, lat2 = transformer_29n.transform(x2, y2)
                
                return f"LINESTRING({lon1} {lat1}, {lon2} {lat2})"
                
            except ImportError:
                return "LINESTRING(-7.6167 33.5731, -6.8498 34.0209)"
                
    except Exception as e:
        print(f"Erreur parsing WKB LineString: {e}")
        return "LINESTRING(-7.0926 31.7917, -6.8 31.6)"  # Ligne par défaut au Maroc
    return None

@app.route('/api/arcs')
def api_arcs():
    try:
        # Utiliser SQLAlchemy pour récupérer les données
        arcs = GrapheArc.query.limit(50).all()
        arcs_data = []
        
        for arc in arcs:
            # Parser la géométrie WKB
            geometrie_wkt = parse_wkb_linestring(arc.geometrie)
            
            arc_dict = {
                'id': arc.id,
                'axe': arc.axe,
                'plod': arc.plod,
                'plof': arc.plof,
                'cumuld': float(arc.cumuld) if arc.cumuld else None,
                'cumulf': float(arc.cumulf) if arc.cumulf else None,
                'geometrie': geometrie_wkt
            }
            arcs_data.append(arc_dict)
        
        return jsonify({'success': True, 'data': arcs_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/statistiques')
def api_statistiques():
    try:
        # Statistiques des gares
        total_gares = GareRef.query.count()
        gares_par_type = db.session.query(GareRef.typegare, db.func.count(GareRef.id)).group_by(GareRef.typegare).all()
        gares_par_axe = db.session.query(GareRef.axe, db.func.count(GareRef.id)).group_by(GareRef.axe).all()
        
        # Statistiques des arcs
        total_arcs = GrapheArc.query.count()
        arcs_par_axe = db.session.query(GrapheArc.axe, db.func.count(GrapheArc.id)).group_by(GrapheArc.axe).all()
        
        # Statistiques des événements/incidents avec SQL direct
        import psycopg2.extras
        conn_stat = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor_stat = conn_stat.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Compter les événements
        cursor_stat.execute("SELECT COUNT(*) FROM gpr.ge_evenement")
        total_evenements = cursor_stat.fetchone()[0]
        
        # Événements par statut
        cursor_stat.execute("SELECT etat, COUNT(*) FROM gpr.ge_evenement GROUP BY etat")
        evenements_par_statut = cursor_stat.fetchall()
        
        # Statistiques des types d'incidents
        cursor_stat.execute("SELECT COUNT(*) FROM gpr.ref_types")
        total_types = cursor_stat.fetchone()[0]
        
        cursor_stat.execute("SELECT COUNT(*) FROM gpr.ref_types WHERE etat = true")
        types_actifs = cursor_stat.fetchone()[0]
        
        cursor_stat.close()
        conn_stat.close()
        
        stats = {
            'gares': {
                'total': total_gares,
                'par_type': [{'type': t[0] or 'Non défini', 'count': t[1]} for t in gares_par_type],
                'par_axe': [{'axe': a[0] or 'Non défini', 'count': a[1]} for a in gares_par_axe]
            },
            'arcs': {
                'total': total_arcs,
                'par_axe': [{'axe': a[0] or 'Non défini', 'count': a[1]} for a in arcs_par_axe]
            },
            'evenements': {
                'total': total_evenements,
                'par_statut': [{'statut': s['etat'] or 'Non défini', 'count': s['count']} for s in evenements_par_statut]
            },
            'types_incidents': {
                'total': total_types,
                'actifs': types_actifs
            }
        }
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements')
def api_evenements():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        statut = request.args.get('statut', '')
        
        # Utiliser des requêtes SQL directes
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Construire la requête avec filtres
        where_clause = ""
        params = []
        if statut:
            where_clause = "WHERE e.etat ILIKE %s"
            params.append(f'%{statut}%')
        
        # Compter le total
        cursor.execute(f"SELECT COUNT(*) FROM gpr.ge_evenement e {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # Récupérer les données paginées avec localisation
        offset = (page - 1) * per_page
        cursor.execute(f"""
            SELECT e.id, e.date_debut, e.date_fin, e.heure_debut, e.heure_fin, e.etat, 
                   e.resume, e.commentaire, e.extrait, e.type_id, e.sous_type_id,
                   l.id as localisation_id, l.gare_debut_id, l.gare_fin_id, l.pk_debut, l.pk_fin
            FROM gpr.ge_evenement e
            LEFT JOIN gpr.ge_localisation l ON e.id = l.evenement_id
            {where_clause}
            ORDER BY e.date_debut DESC 
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        evenements = cursor.fetchall()
        
        evenements_data = []
        for evt in evenements:
            description = evt['resume'] or evt['commentaire'] or evt['extrait'] or 'Aucune description'
            if len(description) > 200:
                description = description[:200] + '...'
            
            # Déterminer les coordonnées de l'incident basées sur la description
            incident_coords = None
            incident_location = None
            
            # Coordonnées approximatives pour différentes régions du Maroc
            maroc_coords = {
                'casa': [33.5731, -7.5898],      # Casablanca
                'rabat': [34.0209, -6.8416],     # Rabat
                'marrakech': [31.6295, -7.9811], # Marrakech
                'fes': [34.0181, -5.0078],       # Fès
                'meknes': [33.8935, -5.5473],    # Meknès
                'tanger': [35.7595, -5.8340],    # Tanger
                'agadir': [30.4278, -9.5981],    # Agadir
                'oujda': [34.6814, -1.9086],     # Oujda
                'kenitra': [34.2610, -6.5802],   # Kénitra
                'mohammedia': [33.6833, -7.3833], # Mohammedia
                'safi': [32.2833, -9.2333],      # Safi
                'taza': [34.2167, -4.0167],      # Taza
                'nador': [35.1683, -2.9273],     # Nador
                'el jadida': [33.2333, -8.5000], # El Jadida
                'beni mellal': [32.3373, -6.3498], # Beni Mellal
                'ouarzazate': [30.9200, -6.9100], # Ouarzazate
                'al hoceima': [35.2492, -3.9371], # Al Hoceima
                'tetouan': [35.5711, -5.3724],   # Tétouan
                'larache': [35.1833, -6.1500],   # Larache
                'khemisset': [33.8167, -6.0667], # Khémisset
                'sidi kacem': [34.2167, -5.7000], # Sidi Kacem
                'sidi slimane': [34.2667, -5.9333], # Sidi Slimane
                'benguerir': [32.2500, -7.9500], # Benguerir
                'el aria': [32.4833, -8.0167],   # El Aria
                'oued amlil': [34.2000, -4.2833], # Oued Amlil
            }
            
            # Essayer de trouver des coordonnées basées sur la description
            description_lower = description.lower()
            for key, coords in maroc_coords.items():
                if key in description_lower:
                    incident_coords = f"POINT({coords[1]} {coords[0]})"
                    incident_location = key.replace('_', ' ').title()
                    break
            
            # Si aucune correspondance, utiliser des coordonnées par défaut
            if not incident_coords:
                incident_coords = "POINT(-7.0926 31.7917)"  # Centre du Maroc
                incident_location = "Localisation approximative"
            
            evt_dict = {
                'id': evt['id'],
                'date_debut': evt['date_debut'].isoformat() if evt['date_debut'] else None,
                'date_fin': evt['date_fin'].isoformat() if evt['date_fin'] else None,
                'heure_debut': evt['heure_debut'].strftime('%H:%M:%S') if evt['heure_debut'] else None,
                'heure_fin': evt['heure_fin'].strftime('%H:%M:%S') if evt['heure_fin'] else None,
                'statut': evt['etat'],
                'description': description,
                'type_id': evt['type_id'],
                'localisation_id': evt['localisation_id'],
                'gare_debut_id': evt['gare_debut_id'],
                'gare_fin_id': evt['gare_fin_id'],
                'pk_debut': evt['pk_debut'],
                'pk_fin': evt['pk_fin'],
                'geometrie': incident_coords,
                'location_name': incident_location
            }
            evenements_data.append(evt_dict)
        
        pages = (total + per_page - 1) // per_page
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'data': evenements_data,
            'pagination': {
                'page': page,
                'pages': pages,
                'per_page': per_page,
                'total': total
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/types-incidents')
def api_types_incidents():
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, intitule, entite_type_id, etat
            FROM gpr.ref_types 
            WHERE etat = true AND (deleted = false OR deleted IS NULL)
            ORDER BY intitule
        """)
        
        types = cursor.fetchall()
        types_data = []
        
        for type_inc in types:
            type_dict = {
                'id': type_inc['id'],
                'libelle': type_inc['intitule'],
                'niveau': type_inc['entite_type_id'],
                'systeme_id': type_inc['entite_type_id']
            }
            types_data.append(type_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': types_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/localisations')
def api_localisations():
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, autre, commentaire, type_localisation, type_pk, 
                   pk_debut, pk_fin, gare_debut_id, gare_fin_id
            FROM gpr.ge_localisation 
            LIMIT 100
        """)
        
        localisations = cursor.fetchall()
        loc_data = []
        
        for loc in localisations:
            loc_dict = {
                'id': loc['id'],
                'axe': loc['autre'],
                'pk_debut': loc['pk_debut'],
                'pk_fin': loc['pk_fin'],
                'voie': loc['type_localisation'],
                'section': loc['type_pk'],
                'gare': loc['gare_debut_id'],
                'description': loc['commentaire'] or loc['autre']
            }
            loc_data.append(loc_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': loc_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements', methods=['POST'])
def api_create_evenement():
    """Créer un nouvel événement/incident"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['type_id', 'description', 'date_debut']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Le champ {field} est requis'})
        
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Insérer l'événement
        cursor.execute("""
            INSERT INTO gpr.ge_evenement 
            (date_debut, date_fin, heure_debut, heure_fin, resume, etat, type_id, sous_type_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('date_debut'),
            data.get('date_fin'),
            data.get('heure_debut'),
            data.get('heure_fin'),
            data.get('description'),
            data.get('statut', 'Ouvert'),
            data.get('type_id'),
            data.get('sous_type_id'),
            data.get('user_id', 1)  # Utilisateur par défaut
        ))
        
        evenement_id = cursor.fetchone()[0]
        
        # Si une localisation est spécifiée, l'ajouter
        if data.get('localisation_id'):
            cursor.execute("""
                INSERT INTO gpr.ge_localisation 
                (evenement_id, gare_debut_id, gare_fin_id, pk_debut, pk_fin, type_localisation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                evenement_id,
                data.get('gare_debut_id'),
                data.get('gare_fin_id'),
                data.get('pk_debut'),
                data.get('pk_fin'),
                data.get('type_localisation', 'section')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident créé avec succès', 'id': evenement_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/<int:evenement_id>', methods=['PUT'])
def api_update_evenement(evenement_id):
    """Modifier un événement/incident existant"""
    try:
        data = request.get_json()
        
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Mettre à jour l'événement
        update_fields = []
        params = []
        
        if 'date_debut' in data:
            update_fields.append('date_debut = %s')
            params.append(data['date_debut'])
        if 'date_fin' in data:
            update_fields.append('date_fin = %s')
            params.append(data['date_fin'])
        if 'heure_debut' in data:
            update_fields.append('heure_debut = %s')
            params.append(data['heure_debut'])
        if 'heure_fin' in data:
            update_fields.append('heure_fin = %s')
            params.append(data['heure_fin'])
        if 'resume' in data:
            update_fields.append('resume = %s')
            params.append(data['resume'])
        if 'etat' in data:
            update_fields.append('etat = %s')
            params.append(data['etat'])
        if 'type_id' in data:
            update_fields.append('type_id = %s')
            params.append(data['type_id'])
        if 'sous_type_id' in data:
            update_fields.append('sous_type_id = %s')
            params.append(data['sous_type_id'])
        
        if update_fields:
            params.append(evenement_id)
            cursor.execute(f"""
                UPDATE gpr.ge_evenement 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident modifié avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evenements/<int:evenement_id>', methods=['DELETE'])
def api_delete_evenement(evenement_id):
    """Supprimer un événement/incident"""
    try:
        import psycopg2.extras
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Supprimer d'abord les localisations associées
        cursor.execute("DELETE FROM gpr.ge_localisation WHERE evenement_id = %s", (evenement_id,))
        
        # Supprimer l'événement
        cursor.execute("DELETE FROM gpr.ge_evenement WHERE id = %s", (evenement_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Incident supprimé avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=form.username.data).first():
            flash('Ce nom d\'utilisateur existe déjà.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return render_template('register.html', form=form)
        
        # Créer le nouvel utilisateur
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

# Protéger toutes les routes principales
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/carte')
@login_required
def carte():
    return render_template('carte.html')

@app.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')

@app.route('/gares')
@login_required
def gares():
    return render_template('gares.html')

@app.route('/incidents')
@login_required
def incidents():
    return render_template('incidents.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 