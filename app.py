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
@app.route('/api/gares')
def api_gares():
    try:
        gares = GareRef.query.limit(100).all()
        gares_data = []
        
        for gare in gares:
            gare_dict = {
                'id': gare.id,
                'nom': gare.nomgarefr,
                'code': gare.codegare,
                'type': gare.typegare,
                'axe': gare.axe,
                'ville': gare.villes_ville,
                'etat': gare.etat,
                'geometrie': gare.geometrie
            }
            gares_data.append(gare_dict)
        
        return jsonify({'success': True, 'data': gares_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/arcs')
def api_arcs():
    try:
        arcs = GrapheArc.query.limit(50).all()
        arcs_data = []
        
        for arc in arcs:
            arc_dict = {
                'id': arc.id,
                'axe': arc.axe,
                'plod': arc.plod,
                'plof': arc.plof,
                'cumuld': float(arc.cumuld) if arc.cumuld else None,
                'cumulf': float(arc.cumulf) if arc.cumulf else None,
                'geometrie': arc.geometrie
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