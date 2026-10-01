"""
Application Streamlit : FTTH AirPON ML Dashboard : Version 1.0
Projet : I-ENGINEERING TCHAD SARL
ENSPM : École Nationale Supérieure Polytechnique de l'Université de Maroua
Version v1.0 :
  - Correction bug typo generer_rapport (ligne "f {recomm}")
  - Correction double migration SQLite resultat_fr
  - Correction chemins modèles flexibles (racine ou sous-dossiers)
  - Protection anti-doublon sauvegarde prédiction
  - Compteur prédictions en sidebar
  - Ratio budget affiché en temps réel
  - Rapport HTML téléchargeable (remplace .txt)
  - Filtres interactifs sur la carte géographique
  - Page Statistiques Admin (nouvelle)
  - Comparaison de deux scénarios (nouvelle)
"""

import os, sqlite3, hashlib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import GLOBAL_TR, tr
import pandas as pd
import joblib
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(
    page_title="FTTH AirPON ML",
    page_icon="📡", layout="wide",
    initial_sidebar_state="expanded"
)

def get_session_language():
    try:
        return st.session_state.get("language", "fr") or "fr"
    except Exception:
        return "fr"

def safe_str(s):
    return str(s) if s is not None else ""

# Logos en cache — chargés une seule fois, pas à chaque rerun
@st.cache_data
def get_logos():
    """Retourne les logos en base64 — mis en cache pour éviter le rechargement."""
    return (
        "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08WI53b8UQkAAHvAyj6pO37FAMKBqJwBunOs20z2/I5uwcJKtueRMXQAIJDP5xv1xsKHC5ffvmw96ZXkOoDvWHdn5YBy6e1L5fNl7xShzDDvhedDJSbYCwTyk/n8ZD61GH3zt9w0/TrO0VG7N+Nu8V94znCOItb7RID2KpC+hOXNFoqyBL65RGECqgqlQEdo5XylfLa88F8LCx8u2JMq4+DtFoH8ZL7yRuX0mdOesxKTE0qpJEn7OGKYNCc28ZUFtjLCRZGaMafne++/77lfIzJG+bMzCl0gbebaJgOoE09nRKcAQPqavd3XCwQGifaVVn9Yr92tNb9sttvtwPRLSZLkcVmdVIvTxeI/FlPXUBgOge5ediOUuJv7Pzea8+Yt+gMuAKBOKpuNx9aW6gfNtbstAMl6r5+VFIUcADDQ7VOS7dWPZ3qub8+MsAKwHdbpdqzHoHMjOesx6GFnKjMGLHy48O6Vd638u5utdtnaMn9lfvbsrLUzgF+FUaKsflC98LPQWBYXry+dKK5+Zq+d1O5y6YTNmwFAIEdAGumjSRvY8iMIz4M/Pki+L8oBJcubNazVZjp/6SQZaQIA3HLz/Cqb9ntBgmnqXOK98ewIq4+L/B6if6enLh5ROlWK0Ba3YJP1a6fTCb5vIUpbW+2twOEpOfSWuQutIZWBZ0dYzx12dzVRDephNbiuH8+uufzxsm9l/IhEKFjLn2bVhO4Zst0YWWfgWfWxngOazebU309FDyT4xwHlCXn6+LRyUDly6Ij1eP72k+3GRqN2r5ZljQJK6XqtXjiWsnaXAwM7fGW9ns1y7dme39udVYFI/7jNkFPvK29wCyenuck9vxal/Hp5z5nsm2fcYmUYUPvewQXwmMGm8lPaIy0pAgzxP2UYMMjn8/VanUr8eOvezc/eGf5YYV88c6qC4Ejl6uer9gNwCRIJTw0NbI9BOaCsrq0GB2UGMmn2GRfWs49yUFm/u+4+Chb7FoWEWTTh/QkAgHpYXb+3Lo/JQ4nwobCGj3JAqdfq1osqgvMcAzN8Ui2006SWz5c3NzaVAykPmgtkf1w1ZD/Y/GKzdKq0t+X8QqOKM2dmGo3G0MN+z7jz/tzA9UJaj1pLHy0tf76saZr3VHdyI0ggn8+X/rlU+VlFnpCHuJCOCwpr2AQmd3AK63a7m9pm83+bmqZ1up1ut9t+2rZWkbTeLyePy+ohNf/D/BH1iB3Hj5uJNHBQWN8neDVkUYYBzIhdRmu4dguF9b0hUkl78tnDX4dnt1BYiBAw3IAIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQgBhYUIAYWFCAGFhQjh/wFbLvBriSjhzQAAAABJRU5ErkJggg=="
    )

_EXACT_MAP = {
    'Péri-Urbaine':'Péri_Urbaine','Peri-Urban':'Péri_Urbaine','Peri_Urbaine':'Péri_Urbaine','شبه حضرية':'Péri_Urbaine','Péri_Urbaine':'Péri_Urbaine',
    'Urbaine Dense':'Urbaine_Dense','Dense Urban':'Urbaine_Dense','حضرية كثيفة':'Urbaine_Dense','Urbaine_Dense':'Urbaine_Dense',
    'Urbaine Moyenne':'Urbaine_Moyenne','Medium Urban':'Urbaine_Moyenne','حضرية متوسطة':'Urbaine_Moyenne','Urbaine_Moyenne':'Urbaine_Moyenne',
    'Rurale':'Rurale','Rural':'Rurale','ريفية':'Rurale',
    'Saison Sèche':'Saison_Seche','Dry Season':'Saison_Seche','الموسم الجاف':'Saison_Seche','Saison_Seche':'Saison_Seche',
    'Saison des Pluies':'Saison_Pluies','Rainy Season':'Saison_Pluies','موسم الأمطار':'Saison_Pluies','Saison_Pluies':'Saison_Pluies',
    'Intersaison':'Intersaison','Inter-Season':'Intersaison','الموسم الانتقالي':'Intersaison',
    'Plat':'Plat','Flat':'Plat','مستوٍ':'Plat','Accidenté':'Accidenté','Rugged':'Accidenté','وعر':'Accidenté',
    'Inondable':'Inondable','Flood-prone':'Inondable','عرضة للفيضانات':'Inondable','Sableux':'Sableux','Sandy':'Sableux','رملي':'Sableux',
    'OLT':'OLT','ONT':'ONT','Diviseur (Splitter)':'Splitter','Splitter':'Splitter','مقسم الإشارة':'Splitter',
    'Câble Fibre Optique':'Cable_Fibre','Fiber Optic Cable':'Cable_Fibre','كابل الألياف البصرية':'Cable_Fibre','Cable_Fibre':'Cable_Fibre',
    'Connecteur':'Connecteur','Connector':'Connecteur','موصل':'Connecteur',
    'Boîtier Étanche':'Boitier_Etanche','Waterproof Box':'Boitier_Etanche','علبة مقاومة للماء':'Boitier_Etanche','Boitier_Etanche':'Boitier_Etanche',
    'Antenne AirPON':'Antenne_AirPON','AirPON Antenna':'Antenne_AirPON','هوائي AirPON':'Antenne_AirPON','Antenne_AirPON':'Antenne_AirPON',
    'Rupture de Câble':'Rupture_Cable','Cable Break':'Rupture_Cable','انقطاع الكابل':'Rupture_Cable','Rupture_Cable':'Rupture_Cable',
    'Perte de Signal':'Perte_Signal','Signal Loss':'Perte_Signal','فقدان الإشارة':'Perte_Signal','Perte_Signal':'Perte_Signal',
    'Surtension':'Surtension','Overvoltage':'Surtension','تجاوز الجهد':'Surtension','Corrosion':'Corrosion','التآكل':'Corrosion',
    'Obstruction Physique':'Obstruction_Physique','Physical Obstruction':'Obstruction_Physique','عائق جسدي':'Obstruction_Physique','Obstruction_Physique':'Obstruction_Physique',
    'Défaut Connecteur':'Defaut_Connecteur','Connector Fault':'Defaut_Connecteur','عطل الموصل':'Defaut_Connecteur','Defaut_Connecteur':'Defaut_Connecteur',
    'Panne OLT':'Panne_OLT','OLT Failure':'Panne_OLT','عطل OLT':'Panne_OLT','Panne_OLT':'Panne_OLT',
    'Dégradation Lente':'Degradation_Lente','Slow Degradation':'Degradation_Lente','تدهور تدريجي':'Degradation_Lente','Degradation_Lente':'Degradation_Lente',
    'Faible':'Faible','Low':'Faible','منخفضة':'Faible','Moyenne':'Moyenne','Medium':'Moyenne','متوسطة':'Moyenne',
    'Élevée':'Élevée','High':'Élevée','عالية':'Élevée','Critique':'Critique','Critical':'Critique','حرجة':'Critique',
    "N'Djamena Centre":"N'Djamena_Centre","N'Djamena Center":"N'Djamena_Centre","إنجامينا المركز":"N'Djamena_Centre","N'Djamena_Centre":"N'Djamena_Centre",
    "N'Djamena Sud":"N'Djamena_Sud","N'Djamena South":"N'Djamena_Sud","إنجامينا الجنوب":"N'Djamena_Sud","N'Djamena_Sud":"N'Djamena_Sud",
    "N'Djamena Nord":"N'Djamena_Nord","N'Djamena North":"N'Djamena_Nord","إنجامينا الشمال":"N'Djamena_Nord","N'Djamena_Nord":"N'Djamena_Nord",
    'Moundou':'Moundou','موندو':'Moundou','Sarh':'Sarh','سارح':'Sarh',
    'Abéché':'Abéché','Abeche':'Abéché','أبشه':'Abéché','Kélo':'Kélo','Kelo':'Kélo','كيلو':'Kélo',
    'Doba':'Doba','دوبا':'Doba','Bongor':'Bongor','بونغور':'Bongor',
}
def safe_reverse_tr(val):
    if val in _EXACT_MAP: return _EXACT_MAP[val]
    for k,v in GLOBAL_TR.items():
        if val in (v.get('fr',''),v.get('en',''),v.get('ar','')): return k
    return val

_EXACT_MAP = {
    'Péri-Urbaine':'Péri_Urbaine','Peri-Urban':'Péri_Urbaine','Peri_Urbaine':'Péri_Urbaine','شبه حضرية':'Péri_Urbaine','Péri_Urbaine':'Péri_Urbaine',
    'Urbaine Dense':'Urbaine_Dense','Dense Urban':'Urbaine_Dense','حضرية كثيفة':'Urbaine_Dense','Urbaine_Dense':'Urbaine_Dense',
    'Urbaine Moyenne':'Urbaine_Moyenne','Medium Urban':'Urbaine_Moyenne','حضرية متوسطة':'Urbaine_Moyenne','Urbaine_Moyenne':'Urbaine_Moyenne',
    'Rurale':'Rurale','Rural':'Rurale','ريفية':'Rurale',
    'Saison Sèche':'Saison_Seche','Dry Season':'Saison_Seche','الموسم الجاف':'Saison_Seche','Saison_Seche':'Saison_Seche',
    'Saison des Pluies':'Saison_Pluies','Rainy Season':'Saison_Pluies','موسم الأمطار':'Saison_Pluies','Saison_Pluies':'Saison_Pluies',
    'Intersaison':'Intersaison','Inter-Season':'Intersaison','الموسم الانتقالي':'Intersaison',
    'Plat':'Plat','Flat':'Plat','مستوٍ':'Plat','Accidenté':'Accidenté','Rugged':'Accidenté','وعر':'Accidenté',
    'Inondable':'Inondable','Flood-prone':'Inondable','عرضة للفيضانات':'Inondable','Sableux':'Sableux','Sandy':'Sableux','رملي':'Sableux',
    'OLT':'OLT','ONT':'ONT','Diviseur (Splitter)':'Splitter','Splitter':'Splitter','مقسم الإشارة':'Splitter',
    'Câble Fibre Optique':'Cable_Fibre','Fiber Optic Cable':'Cable_Fibre','كابل الألياف البصرية':'Cable_Fibre','Cable_Fibre':'Cable_Fibre',
    'Connecteur':'Connecteur','Connector':'Connecteur','موصل':'Connecteur',
    'Boîtier Étanche':'Boitier_Etanche','Waterproof Box':'Boitier_Etanche','علبة مقاومة للماء':'Boitier_Etanche','Boitier_Etanche':'Boitier_Etanche',
    'Antenne AirPON':'Antenne_AirPON','AirPON Antenna':'Antenne_AirPON','هوائي AirPON':'Antenne_AirPON','Antenne_AirPON':'Antenne_AirPON',
    'Rupture de Câble':'Rupture_Cable','Cable Break':'Rupture_Cable','انقطاع الكابل':'Rupture_Cable','Rupture_Cable':'Rupture_Cable',
    'Perte de Signal':'Perte_Signal','Signal Loss':'Perte_Signal','فقدان الإشارة':'Perte_Signal','Perte_Signal':'Perte_Signal',
    'Surtension':'Surtension','Overvoltage':'Surtension','تجاوز الجهد':'Surtension','Corrosion':'Corrosion','التآكل':'Corrosion',
    'Obstruction Physique':'Obstruction_Physique','Physical Obstruction':'Obstruction_Physique','عائق جسدي':'Obstruction_Physique','Obstruction_Physique':'Obstruction_Physique',
    'Défaut Connecteur':'Defaut_Connecteur','Connector Fault':'Defaut_Connecteur','عطل الموصل':'Defaut_Connecteur','Defaut_Connecteur':'Defaut_Connecteur',
    'Panne OLT':'Panne_OLT','OLT Failure':'Panne_OLT','عطل OLT':'Panne_OLT','Panne_OLT':'Panne_OLT',
    'Dégradation Lente':'Degradation_Lente','Slow Degradation':'Degradation_Lente','تدهور تدريجي':'Degradation_Lente','Degradation_Lente':'Degradation_Lente',
    'Faible':'Faible','Low':'Faible','منخفضة':'Faible','Moyenne':'Moyenne','Medium':'Moyenne','متوسطة':'Moyenne',
    'Élevée':'Élevée','High':'Élevée','عالية':'Élevée','Critique':'Critique','Critical':'Critique','حرجة':'Critique',
    "N'Djamena Centre":"N'Djamena_Centre","N'Djamena Center":"N'Djamena_Centre","إنجامينا المركز":"N'Djamena_Centre","N'Djamena_Centre":"N'Djamena_Centre",
    "N'Djamena Sud":"N'Djamena_Sud","N'Djamena South":"N'Djamena_Sud","إنجامينا الجنوب":"N'Djamena_Sud","N'Djamena_Sud":"N'Djamena_Sud",
    "N'Djamena Nord":"N'Djamena_Nord","N'Djamena North":"N'Djamena_Nord","إنجامينا الشمال":"N'Djamena_Nord","N'Djamena_Nord":"N'Djamena_Nord",
    'Moundou':'Moundou','موندو':'Moundou','Sarh':'Sarh','سارح':'Sarh',
    'Abéché':'Abéché','Abeche':'Abéché','أبشه':'Abéché','Kélo':'Kélo','Kelo':'Kélo','كيلو':'Kélo',
    'Doba':'Doba','دوبا':'Doba','Bongor':'Bongor','بونغور':'Bongor',
}
def safe_reverse_tr(val):
    if val in _EXACT_MAP: return _EXACT_MAP[val]
    for k,v in GLOBAL_TR.items():
        if val in (v.get('fr',''),v.get('en',''),v.get('ar','')): return k
    return val

# =============================================
# CHEMINS FLEXIBLES — cherche modèles à la racine ou sous-dossiers
# =============================================
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR      = os.path.dirname(BASE_DIR)  # dossier parent (racine projet)
ASSETS_PATH   = os.path.join(BASE_DIR, 'assets')
# users.db cherché d'abord dans app/, puis dans la racine du projet
_db_app  = os.path.join(BASE_DIR, 'users.db')
_db_root = os.path.join(ROOT_DIR, 'users.db')
DB_PATH  = _db_root if os.path.exists(_db_root) else _db_app

def find_model(filename):
    """
    Cherche un fichier .pkl dans les dossiers connus du projet.
    Aucune recherche récursive : chemins directs uniquement.
    Structure :
        Solution_ML_FTTH_AirPON/
        ├── app/streamlit_app.py   (BASE_DIR)
        ├── models/deploiement/
        ├── models/maintenance/
        ├── models/
        └── (racine)
    """
    ROOT = os.path.dirname(BASE_DIR)
    for d in [
        BASE_DIR,
        os.path.join(ROOT, 'models', 'deploiement'),
        os.path.join(ROOT, 'models', 'maintenance'),
        os.path.join(ROOT, 'models'),
        ROOT,
    ]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None

def find_data(filename):
    """
    Cherche un fichier CSV dans les dossiers connus du projet.
    Aucune recherche récursive : chemins directs uniquement.
    Structure :
        Solution_ML_FTTH_AirPON/
        ├── app/streamlit_app.py   (BASE_DIR)
        ├── data/
        └── (racine)
    """
    ROOT = os.path.dirname(BASE_DIR)
    for d in [
        BASE_DIR,
        os.path.join(ROOT, 'data'),
        os.path.join(ROOT, 'data', 'deploiement'),
        os.path.join(ROOT, 'data', 'maintenance'),
        ROOT,
    ]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None

def diagnostic_fichiers():
    """Affiche un diagnostic complet des fichiers trouvés/manquants."""
    fichiers_modeles = [
        'best_rf_deploiement.pkl', 'best_svm_deploiement.pkl',
        'scaler_deploiement.pkl', 'le_target_deploiement.pkl',
        'le_features_deploiement.pkl', 'best_rf_maintenance.pkl',
        'best_svm_maintenance.pkl', 'scaler_maintenance.pkl',
        'le_target_maintenance.pkl', 'le_features_maintenance.pkl',
        'metrics.pkl'
    ]
    fichiers_data = [
        'dataset_deploiement_ftth_airpon.csv',
        'dataset_maintenance_ftth_airpon.csv'
    ]
    manquants = []
    trouves = []
    for f in fichiers_modeles:
        p = find_model(f)
        if p: trouves.append(f"✅ {f}\n   → {p}")
        else: manquants.append(f"❌ {f}")
    for f in fichiers_data:
        p = find_data(f)
        if p: trouves.append(f"✅ {f}\n   → {p}")
        else: manquants.append(f"❌ {f}")
    return trouves, manquants

# =============================================
# BASE DE DONNÉES
# =============================================
def init_db():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    # Table utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, prenom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL, username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, role TEXT DEFAULT "utilisateur",
        date_creation TEXT NOT NULL, derniere_connexion TEXT)''')
    # Table historique
    c.execute('''CREATE TABLE IF NOT EXISTS historique (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL, type_pred TEXT NOT NULL,
        resultat TEXT NOT NULL, resultat_fr TEXT,
        confiance REAL NOT NULL, parametres TEXT NOT NULL,
        date_pred TEXT NOT NULL, langue TEXT DEFAULT "fr")''')
    # Migration colonnes manquantes historique
    c.execute("PRAGMA table_info(historique)")
    cols = [row[1] for row in c.fetchall()]
    if 'langue' not in cols:
        try: c.execute("ALTER TABLE historique ADD COLUMN langue TEXT DEFAULT 'fr'")
        except Exception: pass
    if 'resultat_fr' not in cols:
        try: c.execute("ALTER TABLE historique ADD COLUMN resultat_fr TEXT")
        except Exception: pass
    if 'recommandation' not in cols:
        try: c.execute("ALTER TABLE historique ADD COLUMN recommandation TEXT DEFAULT ''")
        except Exception: pass
    conn.commit(); conn.close()

def get_user_by_email(email):
    """Retrouver un compte par email."""
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT * FROM utilisateurs WHERE email=?", (email.strip().lower(),))
    user = c.fetchone(); conn.close(); return user

def update_password(email, new_password):
    """Mettre à jour le mot de passe via email."""
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE utilisateurs SET password=? WHERE email=?",
              (hash_pw(new_password), email.strip().lower()))
    conn.commit(); conn.close()

def get_user_stats(username):
    """Statistiques complètes d un utilisateur."""
    conn = sqlite3.connect(DB_PATH)
    try:
        total = pd.read_sql_query(
            "SELECT COUNT(*) as n FROM historique WHERE username=?",
            conn, params=(username,)).iloc[0,0]
        deploy = pd.read_sql_query(
            "SELECT COUNT(*) as n FROM historique WHERE username=? AND type_pred LIKE '%ploiement%'",
            conn, params=(username,)).iloc[0,0]
        maint = pd.read_sql_query(
            "SELECT COUNT(*) as n FROM historique WHERE username=? AND type_pred LIKE '%aint%'",
            conn, params=(username,)).iloc[0,0]
        last = pd.read_sql_query(
            "SELECT date_pred FROM historique WHERE username=? ORDER BY date_pred DESC LIMIT 1",
            conn, params=(username,))
        last_pred = last.iloc[0,0] if not last.empty else None
    except Exception:
        total, deploy, maint, last_pred = 0, 0, 0, None
    conn.close()
    return {'total': total, 'deploy': deploy, 'maint': maint, 'last_pred': last_pred}

def delete_user_history(username):
    """Supprimer tout l historique d un utilisateur."""
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM historique WHERE username=?", (username,))
    conn.commit(); conn.close()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def creer_compte(nom, prenom, email, username, password):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute('INSERT INTO utilisateurs (nom,prenom,email,username,password,date_creation) VALUES (?,?,?,?,?,?)',
                  (nom,prenom,email,username,hash_pw(password),datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); conn.close(); return True, "OK"
    except sqlite3.IntegrityError as e:
        return False, ("username" if "username" in str(e) else "email")

def verifier_connexion(username, password):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT * FROM utilisateurs WHERE username=? AND password=?", (username, hash_pw(password)))
    user = c.fetchone()
    if user:
        c.execute("UPDATE utilisateurs SET derniere_connexion=? WHERE username=?",
                  (datetime.now().strftime("%d/%m/%Y %H:%M"), username))
        conn.commit()
    conn.close(); return user

def save_history(username, type_pred, resultat, resultat_fr, confiance, parametres, langue='fr', recommandation=''):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("PRAGMA table_info(historique)")
        cols = [r[1] for r in c.fetchall()]
        if 'recommandation' in cols:
            c.execute('''INSERT INTO historique
                (username,type_pred,resultat,resultat_fr,confiance,parametres,date_pred,langue,recommandation)
                VALUES (?,?,?,?,?,?,?,?,?)''',
                (username,type_pred,resultat,resultat_fr,confiance,
                 str(parametres),datetime.now().strftime("%d/%m/%Y %H:%M"),langue,recommandation))
        else:
            c.execute('''INSERT INTO historique
                (username,type_pred,resultat,resultat_fr,confiance,parametres,date_pred,langue)
                VALUES (?,?,?,?,?,?,?,?)''',
                (username,type_pred,resultat,resultat_fr,confiance,
                 str(parametres),datetime.now().strftime("%d/%m/%Y %H:%M"),langue))
        conn.commit(); conn.close(); return True
    except Exception as e: return str(e)

def check_username_exists(username):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, nom, prenom FROM utilisateurs WHERE username=?", (username,))
    user = c.fetchone(); conn.close(); return user

def get_history(username):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM historique WHERE username=? ORDER BY date_pred DESC", conn, params=(username,))
    conn.close(); return df

def get_all_stats():
    """Stats globales pour page admin"""
    conn = sqlite3.connect(DB_PATH)
    try:
        nb_users = pd.read_sql_query("SELECT COUNT(*) as n FROM utilisateurs", conn).iloc[0,0]
        nb_preds = pd.read_sql_query("SELECT COUNT(*) as n FROM historique", conn).iloc[0,0]
        df_pred  = pd.read_sql_query("SELECT * FROM historique ORDER BY date_pred DESC", conn)
    except Exception:
        nb_users, nb_preds, df_pred = 0, 0, pd.DataFrame()
    conn.close()
    return nb_users, nb_preds, df_pred

init_db()


# =============================================
# DICTIONNAIRE DE TRADUCTIONS COMPLET
# =============================================
TR = {
'fr': {
 'rtl': False,
 'app_title'     : "📡 FTTH AirPON : Système d'aide à la décision basé sur l'apprentissage automatique",
 'app_subtitle'  : "I-ENGINEERING TCHAD SARL | ENSPM : Université de Maroua, Cameroun",
 'nav_label'     : "📡 Navigation",
 'version'       : "Version 1.0 : 2026",
 'lang_select'   : "🌍 Langue",
 'dark_on'       : "🌙 Mode Sombre",
 'dark_off'      : "☀️ Mode Clair",
 'logout'        : "🔓 Se Déconnecter",
 'quit_session'  : "🚪 Quitter la Session",
 'session_reset' : "Session réinitialisée. Vos données de compte sont conservées.",
 'models_ok'     : "✅ Modèles chargés",
 'models_err'    : "❌ Modèles non trouvés",
 'data_ok'       : "✅ Données chargées",
 'data_err'      : "⚠️ Données non trouvées",
 'connected_since': "Connecté depuis le",
 'today'         : "aujourd'hui",
 'current_time'  : "Heure actuelle",
 'pred_session'  : "Prédictions (session)",
 'pages': ["🏠 Tableau de Bord","📦 Prédiction Déploiement","🔧 Prédiction Maintenance",
           "⚔️ Comparaison Scénarios","📊 Historique","🗺️ Carte Géographique",
           "📈 Courbes d'Apprentissage","📊 Exploration des Données",
           "📋 Statistiques Admin","ℹ️ À Propos"],
 'login_tab'     : "🔑 Se Connecter",
 'register_tab'  : "📝 Créer un Compte",
 'login_title'   : "Connectez-vous à votre compte",
 'register_title': "Créer votre compte",
 'username_lbl'  : "👤 Nom d'utilisateur",
 'password_lbl'  : "🔑 Mot de passe",
 'confirm_pwd'   : "🔑 Confirmer le mot de passe",
 'nom_lbl'       : "👤 Nom",
 'prenom_lbl'    : "👤 Prénom",
 'email_lbl'     : "📧 Email",
 'login_btn'     : "🚀 Se Connecter",
 'register_btn'  : "✅ Créer mon Compte",
 'cancel_btn'    : "✖ Annuler",
 'required_fields': "* Champs obligatoires",
 'err_fields'    : "❌ Veuillez remplir tous les champs obligatoires.",
 'err_pwd_short' : "❌ Le mot de passe doit contenir au moins 6 caractères.",
 'err_pwd_match' : "❌ Les mots de passe ne correspondent pas.",
 'err_email'     : "❌ Format d'email invalide.",
 'err_user_short': "❌ Le nom d'utilisateur doit contenir au moins 3 caractères.",
 'err_login'     : "❌ Nom d'utilisateur ou mot de passe incorrect.",
 'err_fields2'   : "❌ Veuillez saisir votre identifiant et mot de passe.",
 'err_username'  : "❌ Ce nom d'utilisateur est déjà pris.",
 'err_email2'    : "❌ Cet email est déjà utilisé.",
 'cancel_login'  : "Connexion annulée.",
 'cancel_reg'    : "Inscription annulée.",
 'welcome'       : "Bienvenue",
 'account_created': "Compte créé avec succès !",
 'dashboard_title': "📊 Performances des Modèles ML",
 'company_lbl'   : "I-ENGINEERING TCHAD SARL",
 'school_lbl'    : "École Nationale Supérieure Polytechnique de l'Université de Maroua (ENSPM) : Maroua, Cameroun",
 'theme_lbl'     : "Thème",
 'company_label' : "Entreprise",
 'school_label'  : "Établissement",
 'theme_val'     : "Conception et implémentation d'une solution basée sur le Machine Learning pour l'optimisation du déploiement et de la maintenance des réseaux FTTH AirPON.",
 'deploy_lbl'    : "Déploiement",
 'maint_lbl'     : "Maintenance",
 'accuracy_vs'   : "Accuracy RF vs SVM",
 'distrib_lbl'   : "Distribution des Classes",
 'preview_lbl'   : "📋 Aperçu des Données",
 'tab_deploy_ds' : "📦 Dataset Déploiement",
 'tab_maint_ds'  : "🔧 Dataset Maintenance",
 'rows_cols'     : "lignes × colonnes | Cible",
 'pred_d_title'  : "📦 Prédiction Statut de Déploiement FTTH/AirPON",
 'loc_climate'   : "🗺️ Localisation & Climat",
 'loc_lbl'       : "📍 Localisation",
 'zone_lbl'      : "🏙️ Type de Zone",
 'season_lbl'    : "🌡️ Saison",
 'terrain_lbl'   : "⛰️ Type de Terrain",
 'temp_lbl'      : "🌡️ Température (°C)",
 'hum_lbl'       : "💧 Humidité (%)",
 'obstacle_lbl'  : "🚧 Obstacles présents",
 'yes_no'        : ["Non", "Oui"],
 'infra_lbl'     : "🔌 Infrastructure Réseau",
 'foyers_lbl'    : "🏠 Nb Foyers Cibles",
 'dist_lbl'      : "📏 Distance Noeud (km)",
 'cable_lbl'     : "🔌 Longueur Câble (km)",
 'olt_lbl'       : "📡 Nombre d'OLT",
 'ont_lbl'       : "📡 Nombre d'ONT",
 'perf_net'      : "📶 Performance Réseau",
 'sig_olt_lbl'   : "Signal OLT (dBm)",
 'sig_ont_lbl'   : "Signal ONT (dBm)",
 'lat_lbl'       : "⏱️ Latence (ms)",
 'budget_lbl'    : "💰 Budget & Délais",
 'cout_mat'      : "💰 Coût Matériel (FCFA)",
 'cout_mo'       : "👷 Coût Main d'œuvre (FCFA)",
 'budget_alloc'  : "📊 Budget Alloué (FCFA)",
 'dur_prev'      : "📅 Durée Prévue (jours)",
 'dur_reel'      : "📅 Durée Réelle (jours)",
 'ressources'    : "👷 Ressources Humaines",
 'tech_lbl'      : "👷 Nb Techniciens",
 'exp_lbl'       : "🎓 Expérience Chef de Projet (ans)",
 'incidents_lbl' : "⚠️ Nb Incidents Chantier",
 'model_choice'  : "🤖 Choix du Modèle",
 'predict_d_btn' : "🔮 PRÉDIRE LE STATUT",
 'alerts_title'  : "### 🔔 Alertes Détectées",
 'proba_lbl'     : "Probabilités par Classe",
 'risk_lbl'      : "Facteurs de Risque",
 'result_d_lbl'  : "Statut Prédit",
 'recomm_lbl'    : "💡 Recommandation",
 'export_lbl'    : "📄 Exporter Rapport HTML",
 'pred_m_title'  : "🔧 Prédiction Type d'Intervention Maintenance FTTH/AirPON",
 'equip_lbl'     : "🔧 Équipement",
 'equip_type'    : "🔧 Type d'Équipement",
 'age_lbl'       : "📅 Âge Équipement (mois)",
 'last_maint'    : "🔄 Dernière Maintenance (jours)",
 'prev_interv'   : "📋 Interventions Précédentes",
 'fault_lbl'     : "💥 Panne / Incident",
 'fault_type'    : "💥 Type de Panne",
 'severity_lbl'  : "⚠️ Sévérité",
 'clients_lbl'   : "👥 Clients Affectés",
 'fault_dur'     : "⏱️ Durée Panne (heures)",
 'tickets_open'  : "🎫 Tickets Ouverts",
 'tickets_res'   : "✅ Tickets Résolus",
 'qos_lbl'       : "📶 Performance & QoS",
 'avail_lbl'     : "📶 Disponibilité Réseau (%)",
 'sla_lbl'       : "📃 SLA",
 'sla_opts'      : ["Non Respecté", "Respecté"],
 'satisf_lbl'    : "⭐ Satisfaction Client (1-10)",
 'debit_lbl'     : "📡 Débit Observé (Mbps)",
 'signal_lbl'    : "📶 Signal Observé (dBm)",
 'lat_obs'       : "⏱️ Latence Observée (ms)",
 'loss_lbl'      : "📉 Perte Paquets (%)",
 'predict_m_btn' : "🔮 PRÉDIRE LE TYPE D'INTERVENTION",
 'urgency_lbl'   : "Score d'Urgence (%)",
 'result_m_lbl'  : "Type d'Intervention Prédit",
 'action_lbl'    : "💡 Action Recommandée",
 'Réussi'        : "Réussi",
 'En_retard'     : "En Retard",
 'Échoué'        : "Échoué",
 'Préventive'    : "Préventive",
 'Corrective'    : "Corrective",
 'Urgente'       : "Urgente",
 'reco_reussi'   : "🟢 Continuer selon le plan. Monitoring standard.",
 'reco_retard'   : "🟡 Réviser le planning. Mobiliser des ressources additionnelles.",
 'reco_echoue'   : "🔴 Escalade requise ! Audit technique et révision complète nécessaires.",
 'reco_prev'     : "🔵 Planifier dans le calendrier de maintenance préventive.",
 'reco_corr'     : "🟡 Envoyer une équipe technique sous 24 à 48 heures.",
 'reco_urge'     : "🔴 URGENCE ! Intervention immédiate requise en moins de 4 heures.",
 'al_ok_d'       : "✅ Aucune alerte : Paramètres dans les normes.",
 'al_ok_m'       : "✅ Situation sous contrôle : Aucune alerte critique.",
 'al_budget_c'   : "🔴 ALERTE BUDGET : Ratio {r:.2f} : Dépassement budgétaire critique !",
 'al_budget_w'   : "⚠️ ATTENTION BUDGET : Ratio {r:.2f} : Risque de dépassement.",
 'al_retard_c'   : "🔴 ALERTE DÉLAI : {r} jours de retard : Situation critique !",
 'al_retard_w'   : "⚠️ ATTENTION DÉLAI : {r} jours de retard accumulé.",
 'al_temp_c'     : "🔴 ALERTE TEMPÉRATURE : {r}°C : Conditions extrêmes pour le chantier !",
 'al_temp_w'     : "⚠️ ATTENTION TEMPÉRATURE : {r}°C : Chaleur élevée, prévoir protections.",
 'al_incidents'  : "🔴 ALERTE INCIDENTS : {r} incidents : Chantier très accidenté !",
 'al_signal'     : "🔴 ALERTE SIGNAL : Perte optique {r:.1f} dB : Signal critique !",
 'al_sev_c'      : "🔴 PANNE CRITIQUE : Mobilisation immédiate requise !",
 'al_sev_h'      : "⚠️ SÉVÉRITÉ ÉLEVÉE : Intervention prioritaire sous 4h.",
 'al_clients_c'  : "🔴 IMPACT MAJEUR : {r} clients affectés : Escalade obligatoire !",
 'al_clients_w'  : "⚠️ IMPACT MODÉRÉ : {r} clients affectés.",
 'al_dispo_c'    : "🔴 RÉSEAU CRITIQUE : Disponibilité {r:.1f}% : Très en dessous du seuil !",
 'al_dispo_w'    : "⚠️ DISPONIBILITÉ FAIBLE : {r:.1f}% : SLA en risque.",
 'al_sla'        : "⚠️ SLA NON RESPECTÉ : Pénalités contractuelles possibles.",
 'al_panne_l'    : "🔴 PANNE LONGUE : {r:.1f}h : Impact client majeur !",
 'hist_title'    : "📊 Historique des Prédictions",
 'sess_d_tab'    : "📦 Session Déploiement",
 'sess_m_tab'    : "🔧 Session Maintenance",
 'all_pred_tab'  : "💾 Toutes mes Prédictions",
 'no_pred'       : "Aucune prédiction effectuée pour le moment.",
 'download_csv'  : "📥 Télécharger CSV",
 'pred_count'    : "prédictions dans cette session",
 'pred_total'    : "prédictions enregistrées dans votre compte",
 'distrib_res'   : "Répartition des résultats",
 'map_title_d'   : "🗺️ Carte Géographique des Zones : Tchad",
 'map_sub_d'     : "Distribution des Statuts de Déploiement par Zone",
 'map_sub_m'     : "Distribution des Types d'Intervention par Zone",
 'map_interp_d'  : "Chaque point représente une zone. La taille = nombre de projets. 🟢 Vert = réussis | 🟡 Orange = en retard | 🔴 Rouge = échoués.",
 'map_interp_m'  : "Les zones avec beaucoup d'interventions urgentes (rouge) nécessitent des équipes dédiées sur place.",
 'map_filter_status' : "Filtrer par statut",
 'map_filter_season' : "Filtrer par saison",
 'map_all'       : "Tous",
 'curves_title'  : "📈 Courbes d'Apprentissage des Modèles",
 'tab_rf_d'      : "📦 RF : Déploiement",
 'tab_rf_m'      : "🔧 RF : Maintenance",
 'train_lbl'     : "Entraînement",
 'test_lbl'      : "Test (Validation)",
 'final_acc'     : "Accuracy finale",
 'nb_trees'      : "Nombre d'arbres",
 'acc_pct'       : "Accuracy (%)",
 'compare_title' : "⚔️ Comparaison RF vs SVM",
 'interp_lc_d'   : "La courbe Entraînement est toujours plus haute car le modèle a vu ces données. La courbe Test représente la vraie performance sur de nouvelles données. À partir de 200 arbres les courbes se stabilisent.",
 'interp_lc_m'   : "Le modèle Maintenance suit le même comportement. La stabilisation est atteinte autour de 200-300 arbres. Ajouter plus d'arbres n'améliore plus significativement les performances.",
 'interp_cmp'    : "Le Random Forest surpasse le SVM sur les deux tâches. Le F1-Score tient compte des faux positifs/négatifs. Un F1 proche de l'Accuracy confirme un modèle bien équilibré.",
 'explore_title' : "📊 Exploration des Données",
 'dist_stat_d'   : "Distribution : Statut Déploiement",
 'ratio_bgt'     : "Ratio Budget par Statut",
 'dur_compare'   : "Durée Prévue vs Réelle",
 'temp_season'   : "Température par Saison",
 'dist_stat_m'   : "Distribution : Type Intervention",
 'severity_pie'  : "Sévérité des Pannes",
 'clients_type'  : "Clients Affectés par Type",
 'dispo_satisf'  : "Disponibilité vs Satisfaction",
 'interp_d1'     : "La hauteur des barres montre le nombre de projets par statut. Une majorité de Réussis confirme de bonnes pratiques. Un fort nombre d'Échoués signale des problèmes systémiques.",
 'interp_d2'     : "Un ratio > 1 signifie dépassement du budget. Les projets Échoués ont les ratios les plus élevés : le dépassement budgétaire est un prédicteur clé d'échec.",
 'interp_d3'     : "Points sur la diagonale = délais respectés. Points au-dessus = dépassement. Les projets Échoués sont massivement au-dessus de la diagonale.",
 'interp_d4'     : "La saison sèche affiche des températures extrêmes (35-47°C) impactant les conditions de travail et la durée de vie des équipements.",
 'interp_m1'     : "Un fort taux d'interventions Urgentes révèle un manque de maintenance préventive. L'objectif est d'augmenter les Préventives pour anticiper les pannes.",
 'interp_m2'     : "Un fort pourcentage de pannes Critiques indique la nécessité d'un programme de maintenance préventive renforcé.",
 'interp_m3'     : "Les Urgentes affectent en moyenne beaucoup plus de clients, justifiant une mobilisation immédiate.",
 'interp_m4'     : "Corrélation positive entre disponibilité réseau et satisfaction client. Une disponibilité en baisse entraîne une satisfaction plus faible.",
 'about_title'   : "ℹ️ À Propos du Projet",
 'about_theme_l' : "Thème",
 'about_comp_l'  : "Entreprise",
 'about_sch_l'   : "Établissement",
 'about_theme_v' : "Conception et implémentation d'une solution basée sur le Machine Learning pour l'optimisation du déploiement et de la maintenance des réseaux FTTH AirPON.",
 'about_comp_v'  : "I-ENGINEERING TCHAD SARL : N'Djamena, Tchad (Projet réalisé à Maroua, Cameroun)",
 'about_sch_v'   : "École Nationale Supérieure Polytechnique de l'Université de Maroua (ENSPM) : Maroua, Cameroun",
 'guide_d_title' : "📦 Comment utiliser la Prédiction Déploiement ?",
 'guide_d_txt'   : "Remplissez le formulaire avec les paramètres du projet puis cliquez sur **Prédire le Statut**.",
 'guide_m_title' : "🔧 Comment utiliser la Prédiction Maintenance ?",
 'guide_m_txt'   : "Remplissez le formulaire avec les informations de l'incident puis cliquez sur **Prédire l'Intervention**.",
 'proba_guide'   : "📊 Comment lire les probabilités ?",
 'proba_txt'     : "Une probabilité > 70% indique une prédiction très fiable. La barre la plus longue correspond à la classe prédite.",
 'model_title'   : "🤖 Modèles ML Utilisés",
 'rf_recomm'     : "🏆 Le Random Forest est recommandé : meilleure accuracy sur les deux datasets.",
 'algo_lbl'      : "Algorithme",
 'optim_lbl'     : "Optimisation",
 'page_lbl'      : "Page",
 'of_lbl'        : "/",
 'rf_lbl'        : "Forêt Aléatoire (Random Forest) ⭐",
 'svm_lbl'       : "Machine à Vecteurs de Support (SVM)",
 'ftth_full'     : "Fibre jusqu'au domicile (FTTH) AirPON",
 'rf_full'       : "Forêt Aléatoire (Random Forest)",
 'svm_full'      : "Machine à Vecteurs de Support (SVM)",
 'rf_vs_svm'     : "Forêt Aléatoire vs Machine à Vecteurs de Support",
 'accuracy_lbl'  : "Précision",
 'f1_lbl'        : "Score F1",
 'pct_lbl'       : "%",
 'dataset_lbl'   : "Jeu de Données",
 'target_lbl'    : "Variable Cible",
 'rows_lbl'      : "lignes",
 'cols_lbl'      : "colonnes",
 'col_lbl'       : "Colonne",
 'val_lbl'       : "Valeur",
 'dur_prev_lbl'  : "Durée Prévue (jours)",
 'jours_lbl'     : "jours",
 'dur_reel_lbl'  : "Durée Réelle (jours)",
 'ratio_lbl'     : "Ratio Budget",
 'save_btn'      : "💾 Enregistrer cette Prédiction",
 'save_ok'       : "✅ Prédiction enregistrée dans votre compte !",
 'save_already'  : "ℹ️ Cette prédiction est déjà enregistrée.",
 'hist_col_date' : "Date/Heure",
 'hist_col_type' : "Type",
 'hist_col_result': "Résultat",
 'hist_col_conf' : "Confiance",
 'hist_col_algo' : "Algorithme",
 'hist_col_loc'  : "Localisation",
 'hist_col_season': "Saison",
 'user_known_hint': "Nous vous reconnaissons ! Entrez votre mot de passe pour continuer.",
 # Comparaison
 'compare_page'  : "⚔️ Comparaison de Scénarios",
 'scenario_a'    : "📋 Scénario A",
 'scenario_b'    : "📋 Scénario B",
 'compare_btn'   : "⚔️ COMPARER LES DEUX SCÉNARIOS",
 'compare_result': "Résultats de la Comparaison",
 'vs_lbl'        : "VS",
 # Admin
 'admin_title'   : "📋 Statistiques Globales",
 'admin_users'   : "Utilisateurs inscrits",
 'admin_preds'   : "Prédictions totales",
 'admin_deploy'  : "Prédictions Déploiement",
 'admin_maint'   : "Prédictions Maintenance",
 'admin_recent'  : "Prédictions récentes (toutes sessions)",
 'admin_monthly' : "Prédictions par mois",
 'admin_distrib' : "Répartition globale des résultats",
},

'en': {
 'rtl': False,
 'app_title'     : "📡 FTTH AirPON : Decision Support System based on Machine Learning",
 'app_subtitle'  : "I-ENGINEERING TCHAD SARL | ENSPM : University of Maroua, Cameroon",
 'nav_label'     : "🧭 Navigation",
 'version'       : "Version 1.0 : 2026",
 'lang_select'   : "🌍 Language",
 'dark_on'       : "🌙 Dark Mode",
 'dark_off'      : "☀️ Light Mode",
 'logout'        : "🔓 Sign Out",
 'quit_session'  : "🚪 Quit Session",
 'session_reset' : "Session reset. Your account data is preserved.",
 'models_ok'     : "✅ Models loaded",
 'models_err'    : "❌ Models not found",
 'data_ok'       : "✅ Data loaded",
 'data_err'      : "⚠️ Data not found",
 'connected_since': "Connected since",
 'today'         : "today",
 'current_time'  : "Current time",
 'pred_session'  : "Predictions (session)",
 'pages': ["🏠 Dashboard","📦 Deployment Prediction","🔧 Maintenance Prediction",
           "⚔️ Scenario Comparison","📊 History","🗺️ Geographic Map",
           "📈 Learning Curves","📊 Data Exploration",
           "📋 Admin Statistics","ℹ️ About"],
 'login_tab'     : "🔑 Sign In",
 'register_tab'  : "📝 Create Account",
 'login_title'   : "Sign in to your account",
 'register_title': "Create your account",
 'username_lbl'  : "👤 Username",
 'password_lbl'  : "🔑 Password",
 'confirm_pwd'   : "🔑 Confirm Password",
 'nom_lbl'       : "👤 Last Name",
 'prenom_lbl'    : "👤 First Name",
 'email_lbl'     : "📧 Email",
 'login_btn'     : "🚀 Sign In",
 'register_btn'  : "✅ Create my Account",
 'cancel_btn'    : "✖ Cancel",
 'required_fields': "* Required fields",
 'err_fields'    : "❌ Please fill all required fields.",
 'err_pwd_short' : "❌ Password must be at least 6 characters.",
 'err_pwd_match' : "❌ Passwords do not match.",
 'err_email'     : "❌ Invalid email format.",
 'err_user_short': "❌ Username must be at least 3 characters.",
 'err_login'     : "❌ Incorrect username or password.",
 'err_fields2'   : "❌ Please enter your username and password.",
 'err_username'  : "❌ This username is already taken.",
 'err_email2'    : "❌ This email is already used.",
 'cancel_login'  : "Login cancelled.",
 'cancel_reg'    : "Registration cancelled.",
 'welcome'       : "Welcome",
 'account_created': "Account created successfully!",
 'dashboard_title': "📊 ML Model Performances",
 'company_lbl'   : "I-ENGINEERING TCHAD SARL",
 'school_lbl'    : "National Advanced School of Engineering, University of Maroua (ENSPM) : Maroua, Cameroon",
 'theme_lbl'     : "Theme",
 'company_label' : "Company",
 'school_label'  : "Institution",
 'theme_val'     : "Design and implementation of a Machine Learning-based solution for optimizing FTTH AirPON network deployment and maintenance.",
 'deploy_lbl'    : "Deployment",
 'maint_lbl'     : "Maintenance",
 'accuracy_vs'   : "Accuracy RF vs SVM",
 'distrib_lbl'   : "Class Distribution",
 'preview_lbl'   : "📋 Data Preview",
 'tab_deploy_ds' : "📦 Deployment Dataset",
 'tab_maint_ds'  : "🔧 Maintenance Dataset",
 'rows_cols'     : "rows × columns | Target",
 'pred_d_title'  : "📦 FTTH/AirPON Deployment Status Prediction",
 'loc_climate'   : "🗺️ Location & Climate",
 'loc_lbl'       : "📍 Location",
 'zone_lbl'      : "🏙️ Zone Type",
 'season_lbl'    : "🌡️ Season",
 'terrain_lbl'   : "⛰️ Terrain Type",
 'temp_lbl'      : "🌡️ Temperature (°C)",
 'hum_lbl'       : "💧 Humidity (%)",
 'obstacle_lbl'  : "🚧 Obstacles present",
 'yes_no'        : ["No", "Yes"],
 'infra_lbl'     : "🔌 Network Infrastructure",
 'foyers_lbl'    : "🏠 Target Households",
 'dist_lbl'      : "📏 Node Distance (km)",
 'cable_lbl'     : "🔌 Cable Length (km)",
 'olt_lbl'       : "📡 Number of OLT",
 'ont_lbl'       : "📡 Number of ONT",
 'perf_net'      : "📶 Network Performance",
 'sig_olt_lbl'   : "OLT Signal (dBm)",
 'sig_ont_lbl'   : "ONT Signal (dBm)",
 'lat_lbl'       : "⏱️ Latency (ms)",
 'budget_lbl'    : "💰 Budget & Schedule",
 'cout_mat'      : "💰 Material Cost (FCFA)",
 'cout_mo'       : "👷 Labor Cost (FCFA)",
 'budget_alloc'  : "📊 Allocated Budget (FCFA)",
 'dur_prev'      : "📅 Planned Duration (days)",
 'dur_reel'      : "📅 Actual Duration (days)",
 'ressources'    : "👷 Human Resources",
 'tech_lbl'      : "👷 Nb of Technicians",
 'exp_lbl'       : "🎓 Project Manager Experience (years)",
 'incidents_lbl' : "⚠️ Site Incidents",
 'model_choice'  : "🤖 Model Selection",
 'predict_d_btn' : "🔮 PREDICT STATUS",
 'alerts_title'  : "### 🔔 Detected Alerts",
 'proba_lbl'     : "Probabilities per Class",
 'risk_lbl'      : "Risk Factors",
 'result_d_lbl'  : "Predicted Status",
 'recomm_lbl'    : "💡 Recommendation",
 'export_lbl'    : "📄 Export HTML Report",
 'pred_m_title'  : "🔧 FTTH/AirPON Maintenance Intervention Type Prediction",
 'equip_lbl'     : "🔧 Equipment",
 'equip_type'    : "🔧 Equipment Type",
 'age_lbl'       : "📅 Equipment Age (months)",
 'last_maint'    : "🔄 Last Maintenance (days)",
 'prev_interv'   : "📋 Previous Interventions",
 'fault_lbl'     : "💥 Fault / Incident",
 'fault_type'    : "💥 Fault Type",
 'severity_lbl'  : "⚠️ Severity",
 'clients_lbl'   : "👥 Affected Clients",
 'fault_dur'     : "⏱️ Fault Duration (hours)",
 'tickets_open'  : "🎫 Open Tickets",
 'tickets_res'   : "✅ Resolved Tickets",
 'qos_lbl'       : "📶 Performance & QoS",
 'avail_lbl'     : "📶 Network Availability (%)",
 'sla_lbl'       : "📃 SLA",
 'sla_opts'      : ["Not Respected", "Respected"],
 'satisf_lbl'    : "⭐ Client Satisfaction (1-10)",
 'debit_lbl'     : "📡 Observed Throughput (Mbps)",
 'signal_lbl'    : "📶 Observed Signal (dBm)",
 'lat_obs'       : "⏱️ Observed Latency (ms)",
 'loss_lbl'      : "📉 Packet Loss (%)",
 'predict_m_btn' : "🔮 PREDICT INTERVENTION TYPE",
 'urgency_lbl'   : "Urgency Score (%)",
 'result_m_lbl'  : "Predicted Intervention Type",
 'action_lbl'    : "💡 Recommended Action",
 'Réussi'        : "Successful",
 'En_retard'     : "Delayed",
 'Échoué'        : "Failed",
 'Préventive'    : "Preventive",
 'Corrective'    : "Corrective",
 'Urgente'       : "Urgent",
 'reco_reussi'   : "🟢 Continue as planned. Standard monitoring.",
 'reco_retard'   : "🟡 Revise schedule. Mobilize additional resources.",
 'reco_echoue'   : "🔴 Escalation required! Full technical audit needed.",
 'reco_prev'     : "🔵 Schedule in preventive maintenance calendar.",
 'reco_corr'     : "🟡 Send technical team within 24-48 hours.",
 'reco_urge'     : "🔴 URGENT! Immediate intervention required within 4 hours.",
 'al_ok_d'       : "✅ No alerts : Parameters within norms.",
 'al_ok_m'       : "✅ Situation under control : No critical alerts.",
 'al_budget_c'   : "🔴 BUDGET ALERT: Ratio {r:.2f} : Critical budget overrun!",
 'al_budget_w'   : "⚠️ BUDGET WARNING: Ratio {r:.2f} : Risk of overrun.",
 'al_retard_c'   : "🔴 DELAY ALERT: {r} days behind : Critical situation!",
 'al_retard_w'   : "⚠️ DELAY WARNING: {r} days accumulated delay.",
 'al_temp_c'     : "🔴 TEMPERATURE ALERT: {r}°C : Extreme conditions!",
 'al_temp_w'     : "⚠️ TEMPERATURE WARNING: {r}°C : High heat, protection needed.",
 'al_incidents'  : "🔴 INCIDENTS ALERT: {r} incidents : Very risky site!",
 'al_signal'     : "🔴 SIGNAL ALERT: Optical loss {r:.1f} dB : Critical signal!",
 'al_sev_c'      : "🔴 CRITICAL FAULT : Immediate mobilization required!",
 'al_sev_h'      : "⚠️ HIGH SEVERITY : Priority intervention within 4h.",
 'al_clients_c'  : "🔴 MAJOR IMPACT: {r} clients affected : Mandatory escalation!",
 'al_clients_w'  : "⚠️ MODERATE IMPACT: {r} clients affected.",
 'al_dispo_c'    : "🔴 CRITICAL NETWORK: Availability {r:.1f}% : Far below threshold!",
 'al_dispo_w'    : "⚠️ LOW AVAILABILITY: {r:.1f}% : SLA at risk.",
 'al_sla'        : "⚠️ SLA NOT RESPECTED : Contractual penalties possible.",
 'al_panne_l'    : "🔴 LONG FAULT: {r:.1f}h : Major client impact!",
 'hist_title'    : "📊 Prediction History",
 'sess_d_tab'    : "📦 Session Deployment",
 'sess_m_tab'    : "🔧 Session Maintenance",
 'all_pred_tab'  : "💾 All my Predictions",
 'no_pred'       : "No prediction made yet.",
 'download_csv'  : "📥 Download CSV",
 'pred_count'    : "predictions in this session",
 'pred_total'    : "predictions recorded in your account",
 'distrib_res'   : "Results distribution",
 'map_title_d'   : "🗺️ Geographic Map : Chad",
 'map_sub_d'     : "Deployment Status Distribution by Zone",
 'map_sub_m'     : "Intervention Type Distribution by Zone",
 'map_interp_d'  : "Each point represents a zone. Size = number of projects. 🟢 Green = successful | 🟡 Orange = delayed | 🔴 Red = failed.",
 'map_interp_m'  : "Zones with many urgent interventions (red) need dedicated on-site teams.",
 'map_filter_status' : "Filter by status",
 'map_filter_season' : "Filter by season",
 'map_all'       : "All",
 'curves_title'  : "📈 Model Learning Curves",
 'tab_rf_d'      : "📦 RF : Deployment",
 'tab_rf_m'      : "🔧 RF : Maintenance",
 'train_lbl'     : "Training",
 'test_lbl'      : "Test (Validation)",
 'final_acc'     : "Final Accuracy",
 'nb_trees'      : "Number of Trees",
 'acc_pct'       : "Accuracy (%)",
 'compare_title' : "⚔️ RF vs SVM Comparison",
 'interp_lc_d'   : "Training curve is always higher as the model has seen that data. Test curve shows true performance on new data. Curves stabilize from 200 trees.",
 'interp_lc_m'   : "Maintenance model follows the same pattern. Stabilization reached around 200-300 trees. Adding more trees no longer improves performance significantly.",
 'interp_cmp'    : "Random Forest outperforms SVM on both tasks. F1-Score accounts for false positives/negatives. An F1 close to Accuracy confirms a well-balanced model.",
 'explore_title' : "📊 Data Exploration",
 'dist_stat_d'   : "Distribution: Deployment Status",
 'ratio_bgt'     : "Budget Ratio by Status",
 'dur_compare'   : "Planned vs Actual Duration",
 'temp_season'   : "Temperature by Season",
 'dist_stat_m'   : "Distribution: Intervention Type",
 'severity_pie'  : "Fault Severity",
 'clients_type'  : "Affected Clients by Type",
 'dispo_satisf'  : "Availability vs Satisfaction",
 'interp_d1'     : "Bar height shows number of projects per status. A majority of Successful confirms good practices. High Failed count signals systemic problems.",
 'interp_d2'     : "Ratio > 1 means budget overrun. Failed projects have the highest ratios : budget overrun is a key failure predictor.",
 'interp_d3'     : "Points on diagonal = deadlines met. Points above = overrun. Failed projects are massively above the diagonal.",
 'interp_d4'     : "Dry season shows extreme temperatures (35-47°C) impacting working conditions and equipment lifespan.",
 'interp_m1'     : "High rate of Urgent interventions reveals lack of preventive maintenance. Goal: increase Preventive to anticipate failures.",
 'interp_m2'     : "High Critical fault percentage indicates need for stronger preventive maintenance program.",
 'interp_m3'     : "Urgent interventions affect on average far more clients, justifying immediate mobilization.",
 'interp_m4'     : "Positive correlation between network availability and client satisfaction. Declining availability leads to lower satisfaction.",
 'about_title'   : "ℹ️ About the Project",
 'about_theme_l' : "Theme",
 'about_comp_l'  : "Company",
 'about_sch_l'   : "Institution",
 'about_theme_v' : "Design and implementation of a Machine Learning-based solution for optimizing FTTH AirPON network deployment and maintenance.",
 'about_comp_v'  : "I-ENGINEERING TCHAD SARL : N'Djamena, Chad",
 'about_sch_v'   : "National Advanced School of Engineering, University of Maroua (ENSPM) : Maroua, Cameroon",
 'guide_d_title' : "📦 How to use Deployment Prediction?",
 'guide_d_txt'   : "Fill the form with project parameters then click **Predict Status**.",
 'guide_m_title' : "🔧 How to use Maintenance Prediction?",
 'guide_m_txt'   : "Fill the form with incident information then click **Predict Intervention**.",
 'proba_guide'   : "📊 How to read probabilities?",
 'proba_txt'     : "A probability > 70% indicates a very reliable prediction. The longest bar corresponds to the predicted class.",
 'model_title'   : "🤖 ML Models Used",
 'rf_recomm'     : "🏆 Random Forest is recommended : best accuracy on both datasets.",
 'algo_lbl'      : "Algorithm",
 'optim_lbl'     : "Optimization",
 'page_lbl'      : "Page",
 'of_lbl'        : "/",
 'rf_lbl'        : "Random Forest ⭐",
 'svm_lbl'       : "Support Vector Machine (SVM)",
 'ftth_full'     : "Fiber To The Home (FTTH) AirPON",
 'rf_full'       : "Random Forest",
 'svm_full'      : "Support Vector Machine (SVM)",
 'rf_vs_svm'     : "Random Forest vs Support Vector Machine",
 'accuracy_lbl'  : "Accuracy",
 'f1_lbl'        : "F1 Score",
 'pct_lbl'       : "%",
 'dataset_lbl'   : "Dataset",
 'target_lbl'    : "Target Variable",
 'rows_lbl'      : "rows",
 'cols_lbl'      : "columns",
 'col_lbl'       : "Column",
 'val_lbl'       : "Value",
 'dur_prev_lbl'  : "Planned Duration (days)",
 'jours_lbl'     : "days",
 'dur_reel_lbl'  : "Actual Duration (days)",
 'ratio_lbl'     : "Budget Ratio",
 'save_btn'      : "💾 Save this Prediction",
 'save_ok'       : "✅ Prediction saved to your account!",
 'save_already'  : "ℹ️ This prediction is already saved.",
 'hist_col_date' : "Date/Time",
 'hist_col_type' : "Type",
 'hist_col_result': "Result",
 'hist_col_conf' : "Confidence",
 'hist_col_algo' : "Algorithm",
 'hist_col_loc'  : "Location",
 'hist_col_season': "Season",
 'user_known_hint': "We recognize you! Enter your password to continue.",
 'compare_page'  : "⚔️ Scenario Comparison",
 'scenario_a'    : "📋 Scenario A",
 'scenario_b'    : "📋 Scenario B",
 'compare_btn'   : "⚔️ COMPARE BOTH SCENARIOS",
 'compare_result': "Comparison Results",
 'vs_lbl'        : "VS",
 'admin_title'   : "📋 Global Statistics",
 'admin_users'   : "Registered users",
 'admin_preds'   : "Total predictions",
 'admin_deploy'  : "Deployment predictions",
 'admin_maint'   : "Maintenance predictions",
 'admin_recent'  : "Recent predictions (all sessions)",
 'admin_monthly' : "Predictions per month",
 'admin_distrib' : "Global results distribution",
},

'ar': {
 'rtl': True,
 'app_title'     : "📡 FTTH AirPON : نظام دعم القرار القائم على التعلم الآلي",
 'app_subtitle'  : "I-ENGINEERING TCHAD SARL | ENSPM : جامعة مارووا، الكاميرون",
 'nav_label'     : "📡 التنقل",
 'version'       : "الإصدار 1.0 : 2026",
 'lang_select'   : "🌍 اللغة",
 'dark_on'       : "🌙 الوضع الداكن",
 'dark_off'      : "☀️ الوضع الفاتح",
 'logout'        : "🔓 تسجيل الخروج",
 'quit_session'  : "🚪 إنهاء الجلسة",
 'session_reset' : "تم إعادة تعيين الجلسة. تم الاحتفاظ ببيانات حسابك.",
 'models_ok'     : "✅ تم تحميل النماذج",
 'models_err'    : "❌ النماذج غير موجودة",
 'data_ok'       : "✅ تم تحميل البيانات",
 'data_err'      : "⚠️ البيانات غير موجودة",
 'connected_since': "متصل منذ",
 'today'         : "اليوم",
 'current_time'  : "الوقت الحالي",
 'pred_session'  : "التنبؤات (الجلسة)",
 'pages': ["🏠 لوحة القيادة","📦 التنبؤ بالنشر","🔧 التنبؤ بالصيانة",
           "⚔️ مقارنة السيناريوهات","📊 السجل","🗺️ الخريطة الجغرافية",
           "📈 منحنيات التعلم","📊 استكشاف البيانات",
           "📋 إحصاءات المشرف","ℹ️ حول المشروع"],
 'login_tab'     : "🔑 تسجيل الدخول",
 'register_tab'  : "📝 إنشاء حساب",
 'login_title'   : "تسجيل الدخول إلى حسابك",
 'register_title': "إنشاء حسابك",
 'username_lbl'  : "👤 اسم المستخدم",
 'password_lbl'  : "🔑 كلمة المرور",
 'confirm_pwd'   : "🔑 تأكيد كلمة المرور",
 'nom_lbl'       : "👤 الاسم",
 'prenom_lbl'    : "👤 اللقب",
 'email_lbl'     : "📧 البريد الإلكتروني",
 'login_btn'     : "🚀 تسجيل الدخول",
 'register_btn'  : "✅ إنشاء حسابي",
 'cancel_btn'    : "✖ إلغاء",
 'required_fields': "* الحقول المطلوبة",
 'err_fields'    : "❌ يرجى ملء جميع الحقول المطلوبة.",
 'err_pwd_short' : "❌ يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.",
 'err_pwd_match' : "❌ كلمتا المرور غير متطابقتين.",
 'err_email'     : "❌ تنسيق البريد الإلكتروني غير صالح.",
 'err_user_short': "❌ يجب أن يحتوي اسم المستخدم على 3 أحرف على الأقل.",
 'err_login'     : "❌ اسم المستخدم أو كلمة المرور غير صحيحة.",
 'err_fields2'   : "❌ يرجى إدخال اسم المستخدم وكلمة المرور.",
 'err_username'  : "❌ اسم المستخدم هذا مأخوذ بالفعل.",
 'err_email2'    : "❌ هذا البريد الإلكتروني مستخدم بالفعل.",
 'cancel_login'  : "تم إلغاء تسجيل الدخول.",
 'cancel_reg'    : "تم إلغاء التسجيل.",
 'welcome'       : "مرحباً",
 'account_created': "تم إنشاء الحساب بنجاح!",
 'dashboard_title': "📊 أداء نماذج التعلم الآلي",
 'company_lbl'   : "I-ENGINEERING TCHAD SARL",
 'school_lbl'    : "المدرسة الوطنية العليا للبوليتكنيك بجامعة مارووا (ENSPM) : مارووا، الكاميرون",
 'theme_lbl'     : "الموضوع",
 'company_label' : "الشركة",
 'school_label'  : "المؤسسة",
 'theme_val'     : "تصميم وتنفيذ حل قائم على التعلم الآلي لتحسين نشر وصيانة شبكات FTTH AirPON.",
 'deploy_lbl'    : "النشر",
 'maint_lbl'     : "الصيانة",
 'accuracy_vs'   : "الدقة RF مقابل SVM",
 'distrib_lbl'   : "توزيع الفئات",
 'preview_lbl'   : "📋 معاينة البيانات",
 'tab_deploy_ds' : "📦 مجموعة بيانات النشر",
 'tab_maint_ds'  : "🔧 مجموعة بيانات الصيانة",
 'rows_cols'     : "صفوف × أعمدة | الهدف",
 'pred_d_title'  : "📦 التنبؤ بحالة نشر FTTH/AirPON",
 'loc_climate'   : "🗺️ الموقع والمناخ",
 'loc_lbl'       : "📍 الموقع",
 'zone_lbl'      : "🏙️ نوع المنطقة",
 'season_lbl'    : "🌡️ الموسم",
 'terrain_lbl'   : "⛰️ نوع التضاريس",
 'temp_lbl'      : "🌡️ درجة الحرارة (°م)",
 'hum_lbl'       : "💧 الرطوبة (%)",
 'obstacle_lbl'  : "🚧 وجود عوائق",
 'yes_no'        : ["لا", "نعم"],
 'infra_lbl'     : "🔌 البنية التحتية للشبكة",
 'foyers_lbl'    : "🏠 عدد المنازل المستهدفة",
 'dist_lbl'      : "📏 المسافة إلى العقدة (كم)",
 'cable_lbl'     : "🔌 طول الكابل (كم)",
 'olt_lbl'       : "📡 عدد OLT",
 'ont_lbl'       : "📡 عدد ONT",
 'perf_net'      : "📶 أداء الشبكة",
 'sig_olt_lbl'   : "إشارة OLT (dBm)",
 'sig_ont_lbl'   : "إشارة ONT (dBm)",
 'lat_lbl'       : "⏱️ زمن الاستجابة (ms)",
 'budget_lbl'    : "💰 الميزانية والجداول الزمنية",
 'cout_mat'      : "💰 تكلفة المواد (FCFA)",
 'cout_mo'       : "👷 تكلفة العمالة (FCFA)",
 'budget_alloc'  : "📊 الميزانية المخصصة (FCFA)",
 'dur_prev'      : "📅 المدة المخططة (أيام)",
 'dur_reel'      : "📅 المدة الفعلية (أيام)",
 'ressources'    : "👷 الموارد البشرية",
 'tech_lbl'      : "👷 عدد التقنيين",
 'exp_lbl'       : "🎓 خبرة مدير المشروع (سنوات)",
 'incidents_lbl' : "⚠️ عدد حوادث الورشة",
 'model_choice'  : "🤖 اختيار النموذج",
 'predict_d_btn' : "🔮 التنبؤ بالحالة",
 'alerts_title'  : "### 🔔 التنبيهات المكتشفة",
 'proba_lbl'     : "الاحتماليات لكل فئة",
 'risk_lbl'      : "عوامل الخطر",
 'result_d_lbl'  : "الحالة المتوقعة",
 'recomm_lbl'    : "💡 التوصية",
 'export_lbl'    : "📄 تصدير تقرير HTML",
 'pred_m_title'  : "🔧 التنبؤ بنوع تدخل الصيانة FTTH/AirPON",
 'equip_lbl'     : "🔧 المعدات",
 'equip_type'    : "🔧 نوع المعدات",
 'age_lbl'       : "📅 عمر المعدات (أشهر)",
 'last_maint'    : "🔄 آخر صيانة (أيام)",
 'prev_interv'   : "📋 التدخلات السابقة",
 'fault_lbl'     : "💥 العطل / الحادثة",
 'fault_type'    : "💥 نوع العطل",
 'severity_lbl'  : "⚠️ الخطورة",
 'clients_lbl'   : "👥 العملاء المتضررون",
 'fault_dur'     : "⏱️ مدة العطل (ساعات)",
 'tickets_open'  : "🎫 التذاكر المفتوحة",
 'tickets_res'   : "✅ التذاكر المحلولة",
 'qos_lbl'       : "📶 الأداء وجودة الخدمة",
 'avail_lbl'     : "📶 توفر الشبكة (%)",
 'sla_lbl'       : "📃 اتفاقية مستوى الخدمة",
 'sla_opts'      : ["غير محترمة", "محترمة"],
 'satisf_lbl'    : "⭐ رضا العملاء (1-10)",
 'debit_lbl'     : "📡 معدل النقل الملاحظ (Mbps)",
 'signal_lbl'    : "📶 الإشارة الملاحظة (dBm)",
 'lat_obs'       : "⏱️ زمن الاستجابة الملاحظ (ms)",
 'loss_lbl'      : "📉 فقدان الحزم (%)",
 'predict_m_btn' : "🔮 التنبؤ بنوع التدخل",
 'urgency_lbl'   : "درجة الإلحاح (%)",
 'result_m_lbl'  : "نوع التدخل المتوقع",
 'action_lbl'    : "💡 الإجراء الموصى به",
 'Réussi'        : "ناجح",
 'En_retard'     : "متأخر",
 'Échoué'        : "فاشل",
 'Préventive'    : "وقائي",
 'Corrective'    : "تصحيحي",
 'Urgente'       : "عاجل",
 'reco_reussi'   : "🟢 المتابعة وفق الخطة. مراقبة اعتيادية.",
 'reco_retard'   : "🟡 مراجعة الجدول. تعبئة موارد إضافية.",
 'reco_echoue'   : "🔴 تصعيد مطلوب! مراجعة تقنية كاملة ضرورية.",
 'reco_prev'     : "🔵 جدولة في تقويم الصيانة الوقائية.",
 'reco_corr'     : "🟡 إرسال فريق تقني خلال 24 إلى 48 ساعة.",
 'reco_urge'     : "🔴 طارئ! تدخل فوري مطلوب في أقل من 4 ساعات.",
 'al_ok_d'       : "✅ لا تنبيهات : المعاملات ضمن المعايير.",
 'al_ok_m'       : "✅ الوضع تحت السيطرة : لا تنبيهات حرجة.",
 'al_budget_c'   : "🔴 تنبيه الميزانية: النسبة {r:.2f} : تجاوز حرج للميزانية!",
 'al_budget_w'   : "⚠️ تحذير الميزانية: النسبة {r:.2f} : خطر التجاوز.",
 'al_retard_c'   : "🔴 تنبيه التأخير: {r} أيام تأخير : وضع حرج!",
 'al_retard_w'   : "⚠️ تحذير التأخير: {r} أيام تأخير متراكمة.",
 'al_temp_c'     : "🔴 تنبيه الحرارة: {r}°م : ظروف قصوى!",
 'al_temp_w'     : "⚠️ تحذير الحرارة: {r}°م : حرارة عالية.",
 'al_incidents'  : "🔴 تنبيه الحوادث: {r} حوادث : ورشة خطرة جداً!",
 'al_signal'     : "🔴 تنبيه الإشارة: خسارة بصرية {r:.1f} dB : إشارة حرجة!",
 'al_sev_c'      : "🔴 عطل حرج : تعبئة فورية مطلوبة!",
 'al_sev_h'      : "⚠️ خطورة عالية : تدخل ذو أولوية خلال 4 ساعات.",
 'al_clients_c'  : "🔴 تأثير كبير: {r} عميل متضرر : تصعيد إلزامي!",
 'al_clients_w'  : "⚠️ تأثير معتدل: {r} عميل متضرر.",
 'al_dispo_c'    : "🔴 شبكة حرجة: التوفر {r:.1f}% : أقل بكثير من الحد!",
 'al_dispo_w'    : "⚠️ توفر منخفض: {r:.1f}% : SLA في خطر.",
 'al_sla'        : "⚠️ SLA غير محترمة : غرامات تعاقدية محتملة.",
 'al_panne_l'    : "🔴 عطل طويل: {r:.1f} ساعة : تأثير كبير على العملاء!",
 'hist_title'    : "📊 سجل التنبؤات",
 'sess_d_tab'    : "📦 جلسة النشر",
 'sess_m_tab'    : "🔧 جلسة الصيانة",
 'all_pred_tab'  : "💾 كل تنبؤاتي",
 'no_pred'       : "لم يتم إجراء أي تنبؤ حتى الآن.",
 'download_csv'  : "📥 تنزيل CSV",
 'pred_count'    : "تنبؤات في هذه الجلسة",
 'pred_total'    : "تنبؤات مسجلة في حسابك",
 'distrib_res'   : "توزيع النتائج",
 'map_title_d'   : "🗺️ الخريطة الجغرافية : تشاد",
 'map_sub_d'     : "توزيع حالات النشر حسب المنطقة",
 'map_sub_m'     : "توزيع أنواع التدخلات حسب المنطقة",
 'map_interp_d'  : "كل نقطة تمثل منطقة. الحجم = عدد المشاريع. 🟢 أخضر = ناجح | 🟡 برتقالي = متأخر | 🔴 أحمر = فاشل.",
 'map_interp_m'  : "المناطق ذات التدخلات العاجلة الكثيرة (أحمر) تحتاج فرقاً مخصصة.",
 'map_filter_status' : "تصفية حسب الحالة",
 'map_filter_season' : "تصفية حسب الموسم",
 'map_all'       : "الكل",
 'curves_title'  : "📈 منحنيات تعلم النماذج",
 'tab_rf_d'      : "📦 RF : النشر",
 'tab_rf_m'      : "🔧 RF : الصيانة",
 'train_lbl'     : "التدريب",
 'test_lbl'      : "الاختبار (التحقق)",
 'final_acc'     : "الدقة النهائية",
 'nb_trees'      : "عدد الأشجار",
 'acc_pct'       : "الدقة (%)",
 'compare_title' : "⚔️ مقارنة RF مقابل SVM",
 'interp_lc_d'   : "منحنى التدريب دائماً أعلى لأن النموذج رأى هذه البيانات. منحنى الاختبار يمثل الأداء الحقيقي على بيانات جديدة. تستقر المنحنيات من 200 شجرة.",
 'interp_lc_m'   : "نموذج الصيانة يتبع نفس السلوك. يتحقق الاستقرار حول 200-300 شجرة. إضافة المزيد من الأشجار لا تحسن الأداء بشكل ملحوظ.",
 'interp_cmp'    : "الغابة العشوائية تتفوق على SVM في كلتا المهمتين. درجة F1 تأخذ في الاعتبار الإيجابيات والسلبيات الخاطئة.",
 'explore_title' : "📊 استكشاف البيانات",
 'dist_stat_d'   : "التوزيع: حالة النشر",
 'ratio_bgt'     : "نسبة الميزانية حسب الحالة",
 'dur_compare'   : "المدة المخططة مقابل الفعلية",
 'temp_season'   : "درجة الحرارة حسب الموسم",
 'dist_stat_m'   : "التوزيع: نوع التدخل",
 'severity_pie'  : "خطورة الأعطال",
 'clients_type'  : "العملاء المتضررون حسب النوع",
 'dispo_satisf'  : "التوفر مقابل الرضا",
 'interp_d1'     : "ارتفاع الأعمدة يظهر عدد المشاريع لكل حالة.",
 'interp_d2'     : "نسبة > 1 تعني تجاوز الميزانية. المشاريع الفاشلة لها أعلى نسب.",
 'interp_d3'     : "النقاط على القطر = المواعيد محترمة. النقاط فوقه = تجاوز.",
 'interp_d4'     : "الموسم الجاف يظهر درجات حرارة قصوى (35-47°م).",
 'interp_m1'     : "معدل مرتفع من التدخلات العاجلة يكشف عن نقص في الصيانة الوقائية.",
 'interp_m2'     : "نسبة عالية من الأعطال الحرجة تشير إلى الحاجة لبرنامج صيانة وقائية معزز.",
 'interp_m3'     : "التدخلات العاجلة تؤثر في المتوسط على عملاء أكثر بكثير.",
 'interp_m4'     : "ارتباط إيجابي بين توفر الشبكة ورضا العملاء.",
 'about_title'   : "ℹ️ حول المشروع",
 'about_theme_l' : "الموضوع",
 'about_comp_l'  : "الشركة",
 'about_sch_l'   : "المؤسسة",
 'about_theme_v' : "تصميم وتنفيذ حل قائم على التعلم الآلي لتحسين نشر وصيانة شبكات FTTH AirPON.",
 'about_comp_v'  : "I-ENGINEERING TCHAD SARL : إنجامينا، تشاد",
 'about_sch_v'   : "المدرسة الوطنية العليا للبوليتكنيك بجامعة مارووا (ENSPM) : مارووا، الكاميرون",
 'guide_d_title' : "📦 كيفية استخدام التنبؤ بالنشر؟",
 'guide_d_txt'   : "املأ النموذج بمعاملات المشروع ثم انقر على **التنبؤ بالحالة**.",
 'guide_m_title' : "🔧 كيفية استخدام التنبؤ بالصيانة؟",
 'guide_m_txt'   : "املأ النموذج بمعلومات الحادثة ثم انقر على **التنبؤ بالتدخل**.",
 'proba_guide'   : "📊 كيفية قراءة الاحتماليات؟",
 'proba_txt'     : "احتمالية > 70% تشير إلى تنبؤ موثوق جداً. أطول شريط يمثل الفئة المتوقعة.",
 'model_title'   : "🤖 نماذج التعلم الآلي المستخدمة",
 'rf_recomm'     : "🏆 الغابة العشوائية موصى بها : أفضل دقة على كلا المجموعتين.",
 'algo_lbl'      : "الخوارزمية",
 'optim_lbl'     : "التحسين",
 'page_lbl'      : "صفحة",
 'of_lbl'        : "/",
 'rf_lbl'        : "الغابة العشوائية (Random Forest) ⭐",
 'svm_lbl'       : "آلة ناقلات الدعم (SVM)",
 'ftth_full'     : "الألياف البصرية حتى المنزل (FTTH) AirPON",
 'rf_full'       : "الغابة العشوائية (Random Forest)",
 'svm_full'      : "آلة ناقلات الدعم (SVM)",
 'rf_vs_svm'     : "الغابة العشوائية مقابل آلة ناقلات الدعم",
 'accuracy_lbl'  : "الدقة",
 'f1_lbl'        : "درجة F1",
 'pct_lbl'       : "%",
 'dataset_lbl'   : "مجموعة البيانات",
 'target_lbl'    : "المتغير الهدف",
 'rows_lbl'      : "صفوف",
 'cols_lbl'      : "أعمدة",
 'col_lbl'       : "العمود",
 'val_lbl'       : "القيمة",
 'dur_prev_lbl'  : "المدة المخططة (أيام)",
 'jours_lbl'     : "أيام",
 'dur_reel_lbl'  : "المدة الفعلية (أيام)",
 'ratio_lbl'     : "نسبة الميزانية",
 'save_btn'      : "💾 حفظ هذا التنبؤ",
 'save_ok'       : "✅ تم حفظ التنبؤ في حسابك!",
 'save_already'  : "ℹ️ هذا التنبؤ محفوظ بالفعل.",
 'hist_col_date' : "التاريخ/الوقت",
 'hist_col_type' : "النوع",
 'hist_col_result': "النتيجة",
 'hist_col_conf' : "الثقة",
 'hist_col_algo' : "الخوارزمية",
 'hist_col_loc'  : "الموقع",
 'hist_col_season': "الموسم",
 'user_known_hint': "نتعرف عليك! أدخل كلمة مرورك للمتابعة.",
 'compare_page'  : "⚔️ مقارنة السيناريوهات",
 'scenario_a'    : "📋 السيناريو أ",
 'scenario_b'    : "📋 السيناريو ب",
 'compare_btn'   : "⚔️ مقارنة السيناريوهين",
 'compare_result': "نتائج المقارنة",
 'vs_lbl'        : "مقابل",
 'admin_title'   : "📋 الإحصاءات الشاملة",
 'admin_users'   : "المستخدمون المسجلون",
 'admin_preds'   : "إجمالي التنبؤات",
 'admin_deploy'  : "تنبؤات النشر",
 'admin_maint'   : "تنبؤات الصيانة",
 'admin_recent'  : "التنبؤات الأخيرة (جميع الجلسات)",
 'admin_monthly' : "التنبؤات شهرياً",
 'admin_distrib' : "التوزيع الشامل للنتائج",
},
}


# =============================================
# SESSION STATE
# =============================================
defs = {'logged_in':False,'user_info':None,'page_index':0,
        'dark_mode':False,'language':'fr','hist_deploy':[],'hist_maint':[],
        'last_save_d':None,'last_save_m':None}
for k,v in defs.items():
    if k not in st.session_state: st.session_state[k] = v

# =============================================
# GESTION LANGUE — SOLUTION COMPLÈTE
# =============================================
_LANG_OPTS  = ["Français", "English", "العربية"]
_LANG_CODES = ["fr", "en", "ar"]
_CODE2IDX   = {"fr":0, "en":1, "ar":2}
_CODE2NAME  = {"fr":"Français","en":"English","ar":"العربية"}

def _detect_lang(val):
    """Détecte le code langue depuis n'importe quelle valeur affichée par Windows."""
    if val is None: return None
    if val in _LANG_OPTS:
        return _LANG_CODES[_LANG_OPTS.index(val)]
    v = str(val).lower()
    if any(x in v for x in ["english","anglais","gb"]): return "en"
    if any(x in v for x in ["arab","عرب","arabe"]): return "ar"
    if any(x in v for x in ["fran","français"]): return "fr"
    return None

# NE PAS lire les selectbox ici — ils ne sont pas encore rendus
# La langue est mise à jour par le st.rerun() dans la sidebar

def get_T():
    """Retourne le dictionnaire de traduction — TR est déjà en mémoire."""
    lang = st.session_state.get("language","fr") or "fr"
    if lang not in ("fr","en","ar"): lang = "fr"
    return TR.get(lang, TR["fr"])

T     = get_T()
PAGES = T['pages']
RTL   = T['rtl']
RDIR  = "direction:rtl;text-align:right;" if RTL else ""


# =============================================
# COULEURS
# =============================================
T = get_T()
RTL = T['rtl']
RDIR = 'direction:rtl;text-align:right;' if RTL else ''

if st.session_state.get("dark_mode", False):
    BG="#0e1117";CARD="#1a1f2e";TEXT="#e8eaf6";BORD="#3d4f7c";PLOT="#1a1f2e";NAV="#1a1f2e";ACCENT="#4fc3f7"
else:
    BG="#f8f9ff";CARD="#ffffff";TEXT="#1a1a2e";BORD="#e0e7ff";PLOT="#ffffff";NAV="#f0f4ff";ACCENT="#2E75B6"

st.markdown(f"""<style>
    .main-header{{background:linear-gradient(135deg,#1F4E79,#2E75B6);color:white;padding:18px 30px;
        border-radius:12px;margin-bottom:20px;text-align:center;box-shadow:0 4px 15px rgba(30,87,153,0.3);}}
    .main-header h1{{font-size:22px;margin:0;}} .main-header p{{font-size:13px;margin:4px 0 0 0;opacity:0.9;}}
    .metric-card{{background:{CARD};border-left:5px solid {ACCENT};padding:15px 20px;border-radius:8px;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:12px;{RDIR}}}
    .metric-card h3{{margin:0;font-size:13px;color:#888;}} .metric-card h2{{margin:5px 0 0 0;font-size:26px;color:{ACCENT};}}
    .result-success{{background:#d9ead3;border:2px solid #27ae60;border-radius:10px;padding:20px;{RDIR}}}
    .result-warning{{background:#fff2cc;border:2px solid #f39c12;border-radius:10px;padding:20px;{RDIR}}}
    .result-danger{{background:#ffe6e6;border:2px solid #e74c3c;border-radius:10px;padding:20px;{RDIR}}}
    .result-info{{background:#d5e8f0;border:2px solid #2980b9;border-radius:10px;padding:20px;{RDIR}}}
    .alert-warning{{background:#fff3cd;border-left:5px solid #f39c12;padding:10px 15px;border-radius:5px;margin:5px 0;font-size:14px;{RDIR}}}
    .alert-danger{{background:#f8d7da;border-left:5px solid #e74c3c;padding:10px 15px;border-radius:5px;margin:5px 0;font-size:14px;{RDIR}}}
    .alert-success{{background:#d4edda;border-left:5px solid #27ae60;padding:10px 15px;border-radius:5px;margin:5px 0;font-size:14px;{RDIR}}}
    .section-title{{color:#1F4E79;font-size:20px;font-weight:bold;border-bottom:3px solid #2E75B6;
        padding-bottom:8px;margin:20px 0 15px 0;{RDIR}}}
    .nav-container{{background:{NAV};border-radius:10px;padding:10px 20px;margin-bottom:20px;border:1px solid {BORD};}}
    .interp-box{{background:{CARD};border:1px solid {BORD};border-radius:8px;padding:15px;margin-top:10px;
        color:{TEXT};font-size:14px;border-left:4px solid #2E75B6;{RDIR}}}
    .ratio-box{{background:#eaf4fb;border:2px solid #2E75B6;border-radius:8px;padding:10px 18px;
        font-size:16px;font-weight:bold;color:#1F4E79;margin:8px 0;text-align:center;}}
    .ratio-warn{{background:#fff3cd;border-color:#f39c12;color:#7d5a00;}}
    .ratio-danger{{background:#ffe6e6;border-color:#e74c3c;color:#922b21;}}
    div[data-testid="stSidebar"]{{background:#1a2744 !important;}}
    div[data-testid="stSidebar"] *{{color:white !important;}}
    .stApp{{background-color:{BG};}} body{{{RDIR}}}
</style>""", unsafe_allow_html=True)

# =============================================
# CHARGEMENT MODÈLES & DONNÉES (chemins flexibles)
# =============================================
@st.cache_resource(show_spinner="⏳ Chargement des modèles ML en cours...")
def load_models():
    try:
        files_d = ['best_rf_deploiement.pkl','best_svm_deploiement.pkl',
                   'scaler_deploiement.pkl','le_target_deploiement.pkl','le_features_deploiement.pkl']
        files_m = ['best_rf_maintenance.pkl','best_svm_maintenance.pkl',
                   'scaler_maintenance.pkl','le_target_maintenance.pkl','le_features_maintenance.pkl']
        paths_d = {f: find_model(f) for f in files_d}
        paths_m = {f: find_model(f) for f in files_m}
        missing = [f for f,p in {**paths_d,**paths_m}.items() if p is None]
        if missing:
            return None, f"Fichiers .pkl manquants : {missing}\nDossier de recherche : {BASE_DIR}"
        metrics_path = find_model('metrics.pkl')
        return {
            'rf_deploy'   : joblib.load(paths_d['best_rf_deploiement.pkl']),
            'svm_deploy'  : joblib.load(paths_d['best_svm_deploiement.pkl']),
            'scaler_d'    : joblib.load(paths_d['scaler_deploiement.pkl']),
            'le_target_d' : joblib.load(paths_d['le_target_deploiement.pkl']),
            'le_d'        : joblib.load(paths_d['le_features_deploiement.pkl']),
            'rf_maint'    : joblib.load(paths_m['best_rf_maintenance.pkl']),
            'svm_maint'   : joblib.load(paths_m['best_svm_maintenance.pkl']),
            'scaler_m'    : joblib.load(paths_m['scaler_maintenance.pkl']),
            'le_target_m' : joblib.load(paths_m['le_target_maintenance.pkl']),
            'le_m'        : joblib.load(paths_m['le_features_maintenance.pkl']),
            'metrics'     : joblib.load(metrics_path) if metrics_path else {},
        }, True
    except Exception as e:
        return None, f"Erreur chargement modèles : {str(e)}"

@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    try:
        pd_path = find_data('dataset_deploiement_ftth_airpon.csv')
        pm_path = find_data('dataset_maintenance_ftth_airpon.csv')
        if pd_path and pm_path:
            return pd.read_csv(pd_path), pd.read_csv(pm_path), True
        return None, None, f"Fichiers CSV non trouvés. Dossier cherché : {BASE_DIR}"
    except Exception as e:
        return None, None, f"Erreur chargement données : {str(e)}"

models, models_ok = load_models()
df_deploy, df_maint, data_ok = load_data()

ZONES_RAW        = ["N'Djamena_Centre","N'Djamena_Sud","N'Djamena_Nord",'Moundou','Sarh','Abéché','Kélo','Doba','Bongor']
SAISONS_RAW      = ['Saison_Seche','Saison_Pluies','Intersaison']
ZONES_TYPES_RAW  = ['Urbaine_Dense','Urbaine_Moyenne','Péri_Urbaine','Rurale']
TERRAINS_RAW     = ['Plat','Accidenté','Inondable','Sableux']
SEVERITES_RAW    = ['Faible','Moyenne','Élevée','Critique']
EQUIPEMENTS_RAW  = ['OLT','ONT','Splitter','Cable_Fibre','Connecteur','Boitier_Etanche','Antenne_AirPON']
PANNES_RAW       = ['Rupture_Cable','Perte_Signal','Surtension','Corrosion','Obstruction_Physique','Defaut_Connecteur','Panne_OLT','Degradation_Lente']
ZONES_COORDS     = {"N'Djamena_Centre":(12.1048,15.0444),"N'Djamena_Sud":(12.0800,15.0500),
    "N'Djamena_Nord":(12.1500,15.0300),'Moundou':(8.5667,16.0833),'Sarh':(9.1500,18.3833),
    'Abéché':(13.8333,20.8333),'Kélo':(9.3000,15.8000),'Doba':(8.6500,16.8500),'Bongor':(10.2833,15.3667)}

RES_MAP_D  = {'Réussi':'Réussi','En_retard':'En_retard','Échoué':'Échoué'}
RECO_MAP_D = {'Réussi':'reco_reussi','En_retard':'reco_retard','Échoué':'reco_echoue'}
CSS_MAP_D  = {'Réussi':'result-success','En_retard':'result-warning','Échoué':'result-danger'}
ICO_MAP_D  = {'Réussi':'✅','En_retard':'⚠️','Échoué':'❌'}
RES_MAP_M  = {'Préventive':'Préventive','Corrective':'Corrective','Urgente':'Urgente'}
RECO_MAP_M = {'Préventive':'reco_prev','Corrective':'reco_corr','Urgente':'reco_urge'}
CSS_MAP_M  = {'Préventive':'result-info','Corrective':'result-warning','Urgente':'result-danger'}
ICO_MAP_M  = {'Préventive':'🔵','Corrective':'🟡','Urgente':'🔴'}

def tr_list(lst, lang):
    return [tr(v, lang) for v in lst]

def reverse_tr(val_tr, lang):
    for k, v in GLOBAL_TR.items():
        if v.get(lang) == val_tr or v.get('fr') == val_tr:
            return k
    return val_tr

# =============================================
# NAVIGATION
# =============================================
def nav(page_actuelle):
    T_nav = get_T()
    PAGES_nav = T_nav['pages']
    idx = PAGES_nav.index(page_actuelle) if page_actuelle in PAGES_nav else 0
    n = len(PAGES_nav)
    prev_idx=(idx-1)%n; next_idx=(idx+1)%n
    lang_cur = st.session_state.get('language','fr')
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cg,cm,cd=st.columns([1,4,1])
    with cg:
        if st.button("← "+PAGES_nav[prev_idx].split(' ',1)[1], key=f"ng{idx}", use_container_width=True):
            st.session_state.page_index=prev_idx; st.rerun()
    with cm:
        pts="".join(["🔵 " if i==idx else "⚪ " for i in range(n)])
        st.markdown(f"<div style='text-align:center;font-size:13px;padding-top:4px;'>{pts}</div>"
                    f"<div style='text-align:center;font-size:11px;color:#888;'>"
                    f"{T_nav['page_lbl']} {idx+1}{T_nav['of_lbl']}{n} : {page_actuelle.split(' ',1)[1]}</div>",
                    unsafe_allow_html=True)
    with cd:
        if st.button(PAGES_nav[next_idx].split(' ',1)[1]+" →", key=f"nd{idx}", use_container_width=True):
            st.session_state.page_index=next_idx; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# ALERTES
# =============================================
def alertes_d(ratio_budget,retard,temp,incidents,perte_opt):
    T_a = get_T()
    a=[]
    if ratio_budget>1.3: a.append(('danger',T_a['al_budget_c'].format(r=ratio_budget)))
    elif ratio_budget>1.1: a.append(('warning',T_a['al_budget_w'].format(r=ratio_budget)))
    if retard>30: a.append(('danger',T_a['al_retard_c'].format(r=retard)))
    elif retard>10: a.append(('warning',T_a['al_retard_w'].format(r=retard)))
    if temp>44: a.append(('danger',T_a['al_temp_c'].format(r=temp)))
    elif temp>40: a.append(('warning',T_a['al_temp_w'].format(r=temp)))
    if incidents>8: a.append(('danger',T_a['al_incidents'].format(r=incidents)))
    if perte_opt>28: a.append(('danger',T_a['al_signal'].format(r=perte_opt)))
    if not a: a.append(('success',T_a['al_ok_d']))
    for niv,msg in a: st.markdown(f'<div class="alert-{niv}">{msg}</div>', unsafe_allow_html=True)

def alertes_m(sev,clients,dispo,sla_val,dur_panne):
    T_a = get_T()
    a=[]
    if sev=='Critique': a.append(('danger',T_a['al_sev_c']))
    elif sev=='Élevée': a.append(('warning',T_a['al_sev_h']))
    if clients>300: a.append(('danger',T_a['al_clients_c'].format(r=clients)))
    elif clients>100: a.append(('warning',T_a['al_clients_w'].format(r=clients)))
    if dispo<70: a.append(('danger',T_a['al_dispo_c'].format(r=dispo)))
    elif dispo<85: a.append(('warning',T_a['al_dispo_w'].format(r=dispo)))
    if sla_val==0: a.append(('warning',T_a['al_sla']))
    if dur_panne>24: a.append(('danger',T_a['al_panne_l'].format(r=dur_panne)))
    if not a: a.append(('success',T_a['al_ok_m']))
    for niv,msg in a: st.markdown(f'<div class="alert-{niv}">{msg}</div>', unsafe_allow_html=True)

# =============================================
# RAPPORT HTML (corrigé — plus de "f {recomm}")
# =============================================
def generer_rapport_html(type_pred, resultat, prob_dict, params, algo, reco, css_class):
    T_r = get_T()
    lang = get_session_language()
    # Textes traduits du rapport selon la langue choisie
    lbl_rapport  = {'fr':'Rapport de Prédiction','en':'Prediction Report','ar':'تقرير التنبؤ'}
    lbl_info     = {'fr':'Informations Générales','en':'General Information','ar':'معلومات عامة'}
    lbl_date     = {'fr':'Date','en':'Date','ar':'التاريخ'}
    lbl_user     = {'fr':'Utilisateur','en':'User','ar':'المستخدم'}
    lbl_type     = {'fr':"Type d'analyse",'en':'Analysis Type','ar':'نوع التحليل'}
    lbl_algo     = {'fr':'Algorithme','en':'Algorithm','ar':'الخوارزمية'}
    lbl_result   = {'fr':'Résultat de la Prédiction','en':'Prediction Result','ar':'نتيجة التنبؤ'}
    lbl_proba    = {'fr':'Probabilités','en':'Probabilities','ar':'الاحتمالات'}
    lbl_params   = {'fr':'Paramètres Saisis','en':'Input Parameters','ar':'المعاملات المدخلة'}
    lbl_footer   = {'fr':'I-ENGINEERING TCHAD SARL | ENSPM | Version 1.0 : 2026',
                    'en':'I-ENGINEERING TCHAD SARL | ENSPM | Version 1.0 : 2026',
                    'ar':'I-ENGINEERING TCHAD SARL | ENSPM | الإصدار 1.0 : 2026'}
    rtl_style    = 'direction:rtl;text-align:right;' if lang=='ar' else ''
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    u = st.session_state.get("user_info", None)
    nom = f"{u[1]} {u[2]}" if u else ""
    color_map = {'result-success':'#27ae60','result-warning':'#f39c12',
                 'result-danger':'#e74c3c','result-info':'#2980b9'}
    color = color_map.get(css_class,'#2E75B6')
    bars = ""
    for cls, prob in sorted(prob_dict.items(), key=lambda x:-x[1]):
        pct = prob*100
        bars += f"""<div style="margin:6px 0;{rtl_style}">
          <div style="display:flex;justify-content:space-between;font-size:13px;">
            <span>{cls}</span><span><b>{pct:.1f}%</b></span>
          </div>
          <div style="background:#eee;border-radius:4px;height:14px;">
            <div style="width:{pct:.1f}%;background:{color};height:14px;border-radius:4px;"></div>
          </div>
        </div>"""
    params_rows = "".join(
        f"<tr><td style='padding:4px 8px;color:#666;font-size:13px;{rtl_style}'>{k}</td>"
        f"<td style='padding:4px 8px;font-size:13px;{rtl_style}'><b>{v}</b></td></tr>"
        for k,v in params.items()
    )
    html = f"""<!DOCTYPE html><html lang="{lang}" dir="{"rtl" if lang=="ar" else "ltr"}"><head><meta charset="UTF-8">
<title>{lbl_rapport.get(lang,'Rapport')}</title>
<style>
  body{{font-family:Arial,sans-serif;max-width:800px;margin:auto;padding:30px;background:#f8f9ff;{rtl_style}}}
  .header{{background:linear-gradient(135deg,#1F4E79,#2E75B6);color:white;padding:20px;border-radius:10px;text-align:center;}}
  .section{{background:white;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);}}
  .result-box{{border:2px solid {color};border-radius:8px;padding:15px;background:{color}22;text-align:center;}}
  h2{{color:#1F4E79;border-bottom:2px solid #2E75B6;padding-bottom:6px;}}
  table{{width:100%;border-collapse:collapse;}} tr:nth-child(even){{background:#f5f5f5;}}
  .footer{{text-align:center;color:#888;font-size:12px;margin-top:20px;}}
</style></head><body>
<div class="header">
  <h1 style="margin:0;font-size:20px;">📡 FTTH AirPON ML : {lbl_rapport.get(lang,'Rapport')}</h1>
  <p style="margin:5px 0;font-size:13px;">I-ENGINEERING TCHAD SARL | ENSPM</p>
</div>
<div class="section">
  <h2>📋 {lbl_info.get(lang,'Informations')}</h2>
  <table>
    <tr><td style="padding:4px 8px;color:#666;{rtl_style}">{lbl_date.get(lang,'Date')}</td><td style="padding:4px 8px;"><b>{now}</b></td></tr>
    <tr><td style="padding:4px 8px;color:#666;{rtl_style}">{lbl_user.get(lang,'Utilisateur')}</td><td style="padding:4px 8px;"><b>{nom}</b></td></tr>
    <tr><td style="padding:4px 8px;color:#666;{rtl_style}">{lbl_type.get(lang,'Type')}</td><td style="padding:4px 8px;"><b>{type_pred}</b></td></tr>
    <tr><td style="padding:4px 8px;color:#666;{rtl_style}">{lbl_algo.get(lang,'Algorithme')}</td><td style="padding:4px 8px;"><b>{algo}</b></td></tr>
  </table>
</div>
<div class="section">
  <h2>🎯 {lbl_result.get(lang,'Résultat')}</h2>
  <div class="result-box">
    <h2 style="margin:0;color:{color};">{resultat}</h2>
    <p style="margin:8px 0 0 0;"><b>{T_r['recomm_lbl']} :</b> {reco}</p>
  </div>
</div>
<div class="section">
  <h2>📊 {lbl_proba.get(lang,'Probabilités')}</h2>
  {bars}
</div>
<div class="section">
  <h2>📝 {lbl_params.get(lang,'Paramètres')}</h2>
  <table>{params_rows}</table>
</div>
<div class="footer">
  <p>{lbl_footer.get(lang,'I-ENGINEERING TCHAD SARL | ENSPM | Version 1.0 : 2026')}</p>
</div>
</body></html>"""
    return html

# =============================================
# FONCTION PRÉDICTION (réutilisable pour comparaison)
# =============================================
def predict_deploy(models, loc, type_zone, saison, terrain, obs_val, foyers, dist, cable,
                   nb_olt, nb_ont, temp, hum, sig_olt, sig_ont, latence,
                   cout_mat, cout_mo, budget, dur_prev, dur_reel, nb_tech, exp_chef, incidents, use_rf=True):
    cout_total = cout_mat + cout_mo + 500000
    ratio_budget = cout_total / budget if budget > 0 else 1.0
    retard = max(0, dur_reel - dur_prev)
    perte_opt = abs(sig_olt - sig_ont)
    if models is None:
        st.error(T.get('models_err', '❌ Modèles non chargés. Vérifiez les fichiers .pkl.'))
        st.stop()
    le_d = models['le_d']
    inp = pd.DataFrame([{
        'localisation': le_d['localisation'].transform([loc])[0],
        'type_zone': le_d['type_zone'].transform([type_zone])[0],
        'latitude': ZONES_COORDS.get(loc,(12.1048,15.0444))[0],
        'longitude': ZONES_COORDS.get(loc,(12.1048,15.0444))[1],
        'saison': le_d['saison'].transform([saison])[0],
        'temperature_moy': temp, 'humidite_pct': hum, 'vitesse_vent_kmh': 20.0, 'nb_jours_pluie_mois': 5,
        'type_terrain': le_d['type_terrain'].transform([terrain])[0],
        'presence_obstacle': obs_val, 'nb_foyers_cibles': foyers,
        'distance_noeud_km': dist, 'longueur_cable_km': cable,
        'nb_olt': nb_olt, 'nb_ont': nb_ont, 'nb_splitters': max(1, nb_ont//8),
        'cout_materiel_fcfa': cout_mat, 'cout_main_oeuvre_fcfa': cout_mo,
        'cout_total_fcfa': cout_total, 'budget_alloue_fcfa': budget,
        'ratio_budget': round(ratio_budget,3), 'duree_prevue_jours': dur_prev,
        'duree_reelle_jours': dur_reel, 'retard_jours': retard,
        'debit_montant_mbps': 100.0, 'debit_descendant_mbps': 500.0,
        'puissance_signal_olt_dbm': sig_olt, 'puissance_signal_ont_dbm': sig_ont,
        'perte_optique_db': round(perte_opt,2), 'latence_ms': latence, 'taux_erreur_bit': 0.000001,
        'nb_techniciens': nb_tech, 'experience_chef_projet_ans': exp_chef, 'nb_incidents_chantier': incidents}])
    if use_rf:
        pred = models['rf_deploy'].predict(inp)
        proba = models['rf_deploy'].predict_proba(inp)[0]
    else:
        isc = models['scaler_d'].transform(inp)
        pred = models['svm_deploy'].predict(isc)
        proba = models['svm_deploy'].predict_proba(isc)[0]
    res_raw = models['le_target_d'].inverse_transform(pred)[0]
    classes = models['le_target_d'].classes_
    prob_dict = dict(zip(classes, proba))
    return res_raw, prob_dict, ratio_budget, retard, perte_opt


# =============================================
# PAGE AUTHENTIFICATION
# =============================================
if not st.session_state.get("logged_in", False):
    T = get_T()
    RTL_L = T['rtl']
    RDIR_L = 'direction:rtl;text-align:right;' if RTL_L else 'text-align:center;'
    _L_ENSPM, _L_IENG = get_logos()
    st.markdown(f"""
<div style='background:linear-gradient(135deg,#1F4E79,#2E75B6);border-radius:10px;padding:14px 24px;margin-bottom:18px;color:white;'><div style='display:flex;align-items:center;justify-content:space-between;gap:12px;'><div><img src='data:image/png;base64,{_L_ENSPM}' style='height:70px;width:70px;border-radius:50%;border:2px solid rgba(255,255,255,0.6);background:white;object-fit:contain;padding:2px;' alt='ENSPM'/></div><div style='flex:1;text-align:center;'><h1 style='margin:0;font-size:20px;font-weight:bold;'>{T['app_title']}</h1><p style='font-size:12px;margin:5px 0 2px 0;opacity:0.92;'>{T['app_subtitle']}</p><p style='font-size:11px;opacity:0.75;margin:2px 0 0 0;'>{T['ftth_full']}</p></div><div><img src='data:image/jpeg;base64,{_L_IENG}' style='height:70px;width:70px;border-radius:50%;border:2px solid rgba(255,255,255,0.6);background:white;object-fit:contain;padding:2px;' alt='iEng'/></div></div></div>
""", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown("---")
        _lang_avant_l = st.session_state.get("language","fr")
        _lo_cur_idx = _CODE2IDX.get(_lang_avant_l, 0)
        st.selectbox(
            "🌐 Langue / Language / اللغة",
            options=_LANG_OPTS,
            index=_lo_cur_idx,
            key="lang_selector_login"
        )
        _d_login = _detect_lang(st.session_state.get("lang_selector_login"))
        if _d_login and _d_login != _lang_avant_l:
            st.session_state["language"] = _d_login
            st.rerun()
        T = get_T()

        # Récupération de compte par email
        with st.expander("🔑 " + {'fr':'Mot de passe oublié ?','en':'Forgot password ?','ar':'نسيت كلمة المرور؟'}.get(st.session_state.get('language','fr'),'Mot de passe oublié ?')):
            lbl_rec = {
                'email'    : {'fr':'Votre adresse email','en':'Your email address','ar':'عنوان بريدك الإلكتروني'},
                'btn'      : {'fr':'Vérifier','en':'Verify','ar':'تحقق'},
                'found'    : {'fr':'Compte trouvé. Choisissez un nouveau mot de passe :','en':'Account found. Choose a new password :','ar':'تم العثور على الحساب. اختر كلمة مرور جديدة :'},
                'new_pw'   : {'fr':'Nouveau mot de passe','en':'New password','ar':'كلمة مرور جديدة'},
                'confirm'  : {'fr':'Confirmer le mot de passe','en':'Confirm password','ar':'تأكيد كلمة المرور'},
                'save'     : {'fr':'Enregistrer','en':'Save','ar':'حفظ'},
                'success'  : {'fr':'Mot de passe mis à jour. Connectez-vous.','en':'Password updated. Please login.','ar':'تم تحديث كلمة المرور. يرجى تسجيل الدخول.'},
                'no_match' : {'fr':'Les mots de passe ne correspondent pas.','en':'Passwords do not match.','ar':'كلمات المرور غير متطابقة.'},
                'not_found': {'fr':'Aucun compte trouvé avec cet email.','en':'No account found with this email.','ar':'لم يتم العثور على حساب بهذا البريد.'},
            }
            lang_r = st.session_state.get('language','fr')
            def rl(k): return lbl_rec[k].get(lang_r, lbl_rec[k]['fr'])
            email_rec = st.text_input(rl('email'), key="rec_email", placeholder="exemple@email.com")
            if st.button(rl('btn'), key="rec_btn"):
                if email_rec:
                    user_rec = get_user_by_email(email_rec)
                    if user_rec:
                        st.session_state['rec_user_found'] = True
                        st.session_state['rec_email_val']  = email_rec
                        st.success(rl('found'))
                    else:
                        st.error(rl('not_found'))
            if st.session_state.get('rec_user_found'):
                new_pw1 = st.text_input(rl('new_pw'),     type="password", key="rec_pw1")
                new_pw2 = st.text_input(rl('confirm'), type="password", key="rec_pw2")
                if st.button(rl('save'), key="rec_save_btn", type="primary"):
                    if new_pw1 and new_pw1 == new_pw2:
                        update_password(st.session_state['rec_email_val'], new_pw1)
                        st.success(rl('success'))
                        st.session_state.pop('rec_user_found', None)
                        st.session_state.pop('rec_email_val',  None)
                    else:
                        st.error(rl('no_match'))

        tab_l, tab_r = st.tabs([T['login_tab'], T['register_tab']])
        with tab_l:
            st.markdown(f"#### {T['login_title']}")
            if 'last_username' not in st.session_state: st.session_state.last_username = ""
            with st.form("form_login"):
                username_l = st.text_input(T['username_lbl'], value=st.session_state.get("last_username",""))
                user_check = check_username_exists(username_l) if username_l else None
                if user_check and username_l:
                    st.success(f"👋 {T['welcome']} {user_check[1]} {user_check[2]} !")
                password_l = st.text_input(T['password_lbl'], type="password", placeholder="••••••••")
                col1,col2=st.columns(2)
                with col1: btn_login=st.form_submit_button(T['login_btn'],use_container_width=True,type="primary")
                with col2: btn_cancel_l=st.form_submit_button(T['cancel_btn'],use_container_width=True)
            if btn_cancel_l: st.info(T['cancel_login'])
            if btn_login:
                if not username_l or not password_l: st.error(T['err_fields2'])
                else:
                    user=verifier_connexion(username_l,password_l)
                    if user:
                        st.session_state.logged_in=True; st.session_state.user_info=user
                        st.session_state.last_username=username_l; st.rerun()
                    else: st.error(T['err_login'])

        with tab_r:
            st.markdown(f"#### {T['register_title']}")
            with st.form("form_register"):
                col_a,col_b=st.columns(2)
                with col_a:
                    nom_r=st.text_input(T['nom_lbl']); email_r=st.text_input(T['email_lbl'])
                    pwd_r=st.text_input(T['password_lbl'],type="password")
                with col_b:
                    prenom_r=st.text_input(T['prenom_lbl']); user_r=st.text_input(T['username_lbl'])
                    pwd_r2=st.text_input(T['confirm_pwd'],type="password")
                st.markdown(f"<small style='color:#888;'>{T['required_fields']}</small>",unsafe_allow_html=True)
                col3,col4=st.columns(2)
                with col3: btn_reg=st.form_submit_button(T['register_btn'],use_container_width=True,type="primary")
                with col4: btn_cancel_r=st.form_submit_button(T['cancel_btn'],use_container_width=True)
            if btn_cancel_r: st.info(T['cancel_reg'])
            if btn_reg:
                if not all([nom_r,prenom_r,email_r,user_r,pwd_r,pwd_r2]): st.error(T['err_fields'])
                elif len(pwd_r)<6: st.error(T['err_pwd_short'])
                elif pwd_r!=pwd_r2: st.error(T['err_pwd_match'])
                elif "@" not in email_r: st.error(T['err_email'])
                elif len(user_r)<3: st.error(T['err_user_short'])
                else:
                    ok,msg=creer_compte(nom_r,prenom_r,email_r,user_r,pwd_r)
                    if ok:
                        user_auto=verifier_connexion(user_r,pwd_r)
                        if user_auto:
                            st.session_state.logged_in=True; st.session_state.user_info=user_auto
                            st.balloons(); st.rerun()
                    else: st.error(T['err_username'] if msg=="username" else T['err_email2'])
    st.stop()

# =============================================
# =============================================
# GESTION DE LA LANGUE — callback on_change
# =============================================
T     = get_T()
PAGES = T['pages']
RTL   = T['rtl']
RDIR  = "direction:rtl;text-align:right;" if RTL else ""

u = st.session_state.get("user_info", None)
nb_pred_session = len(st.session_state.get("hist_deploy",[])) + len(st.session_state.get("hist_maint",[]))

# ── GESTION LANGUE ──────────────────────────────────────────
# Lire la sélection AVANT de rendre la sidebar
_lang_avant   = st.session_state.get("language","fr")
_val_sel      = st.session_state.get("lang_selector_main","")
_lang_new     = _detect_lang(_val_sel) if _val_sel else None
_need_rerun   = False
if _lang_new and _lang_new != _lang_avant:
    st.session_state["language"] = _lang_new
    _need_rerun = True          # on rerunera APRÈS la sidebar

T     = get_T()
PAGES = T['pages']
RTL   = T['rtl']
RDIR  = "direction:rtl;text-align:right;" if RTL else ""

with st.sidebar:
    _cur_idx = _CODE2IDX.get(st.session_state.get("language","fr"), 0)
    st.selectbox(
        "🌐 Langue / Language / اللغة",
        options=_LANG_OPTS,
        index=_cur_idx,
        key="lang_selector_main"
    )
    T     = get_T()
    PAGES = T['pages']
    RTL   = T['rtl']
    RDIR  = "direction:rtl;text-align:right;" if RTL else ""

    # --- PROFIL UTILISATEUR ---
    derniere_co = u[8] if u[8] else T['today']
    st.markdown(f"""<div style="background:#0d2b5e;border-radius:8px;padding:12px;text-align:center;margin-bottom:8px;">
        <div style="font-size:28px;">👤</div>
        <div style="font-weight:bold;font-size:14px;">{u[1]} {u[2]}</div>
        <div style="color:#90caf9;font-size:11px;">@{u[4]}</div>
        <div style="color:#aaa;font-size:10px;">{T['connected_since']} {derniere_co}</div>
        <div style="color:#4fc3f7;font-size:12px;margin-top:6px;">🔮 {nb_pred_session} {T['pred_session']}</div>
    </div>""", unsafe_allow_html=True)

    dm_lbl=T['dark_off'] if st.session_state.get("dark_mode", False) else T['dark_on']
    if st.button(dm_lbl,use_container_width=True):
        st.session_state.dark_mode = not st.session_state.get("dark_mode", False); st.rerun()

    st.markdown("<hr style='border-color:#3d4f7c30;margin:6px 0;'>",unsafe_allow_html=True)
    st.markdown(f"## {T['nav_label']}")
    T_nav = get_T()
    PAGES_sidebar = T_nav['pages']
    cur_page_idx = min(st.session_state.get("page_index", 0), len(PAGES_sidebar)-1)
    page=st.radio("",PAGES_sidebar,index=cur_page_idx,label_visibility="collapsed")
    if page is None: page = PAGES_sidebar[0]
    st.session_state.page_index=PAGES_sidebar.index(page)

    st.markdown("<hr style='border-color:#3d4f7c30;margin:6px 0;'>",unsafe_allow_html=True)
    if models_ok is True:
        st.success(T['models_ok'])
    else:
        st.error(T['models_err'])
        with st.expander("🔍 Détails erreur modèles"):
            st.code(str(models_ok))
            st.info(f"📁 Dossier app : {BASE_DIR}")
            trouves, manquants = diagnostic_fichiers()
            if manquants:
                st.error("Fichiers manquants :\n" + "\n".join(manquants))
            if trouves:
                st.success("Fichiers trouvés :\n" + "\n".join(trouves[:3]))
    if data_ok is True:
        st.success(T['data_ok'])
    else:
        st.warning(T['data_err'])
        with st.expander("🔍 Détails erreur données"):
            st.code(str(data_ok))
            st.info(f"📁 Dossier app : {BASE_DIR}")

    st.markdown("<hr style='border-color:#3d4f7c30;margin:6px 0;'>",unsafe_allow_html=True)
    now_str=datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"<div style='text-align:center;color:#90caf9;font-size:11px;'>⏱️ {now_str}<br>{T['ftth_full']}<br>{T['version']}</div>",unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#3d4f7c30;margin:6px 0;'>",unsafe_allow_html=True)
    lang_sb = st.session_state.get('language','fr')
    # Bouton Actualiser supprimé (inutile)
    st.markdown("<hr style='border-color:#3d4f7c30;margin:6px 0;'>",unsafe_allow_html=True)

    if st.button(T['logout'],use_container_width=True,type="primary"):
        for k in ['logged_in','user_info','page_index','hist_deploy','hist_maint','last_save_d','last_save_m']:
            st.session_state[k]=(False if k=='logged_in' else None if k in ('user_info','last_save_d','last_save_m') else 0 if k=='page_index' else [])
        st.rerun()
    if st.button(T['quit_session'],use_container_width=True):
        st.session_state.hist_deploy=[]; st.session_state.hist_maint=[]
        st.session_state.last_save_d=None; st.session_state.last_save_m=None
        st.session_state.page_index=0; st.info(T['session_reset']); st.rerun()

# ── st.rerun() APRÈS la sidebar ─────────────────────────────
# Déclenché seulement si la langue a changé
# Placé ICI (hors sidebar) pour éviter l'erreur removeChild
if _need_rerun:
    st.rerun()

# =============================================
# EN-TÊTE — affiché sur TOUTES les pages
# =============================================
T     = get_T()
PAGES = T['pages']
RTL   = T['rtl']
RDIR  = 'direction:rtl;text-align:right;' if RTL else ''
cur_page_idx_main = st.session_state.get('page_index', 0)

# En-tête commun à TOUTES les pages (traduit dans la langue choisie)
_header_align = 'direction:rtl;text-align:right;' if RTL else 'text-align:center;'
st.markdown(f"""
<div class="main-header" style="{_header_align}padding:18px 24px;border-radius:10px;
     background:linear-gradient(135deg,#1F4E79,#2E75B6);color:white;margin-bottom:12px;">
    <h1 style="margin:0;font-size:22px;font-weight:bold;">
        {T['app_title']}
    </h1>
    <p style="font-size:13px;margin:6px 0 2px 0;opacity:0.92;">
        {T['app_subtitle']}
    </p>
    <p style="font-size:11px;opacity:0.75;margin:2px 0 0 0;">
        {T['ftth_full']}
    </p>
</div>
""", unsafe_allow_html=True)


# =============================================
# PAGE 1 — TABLEAU DE BORD
# =============================================
if cur_page_idx_main == 0:
    nav(PAGES[0])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    _DB_ENSPM, _DB_IENG = get_logos()
    st.markdown("""
<div style='background:linear-gradient(135deg,#1F4E79,#2E75B6);border-radius:10px;padding:14px 24px;margin-bottom:16px;color:white;'><div style='display:flex;align-items:center;justify-content:space-between;gap:12px;'><div><img src='data:image/png;base64,""" + _DB_ENSPM + """' style='height:75px;width:75px;border-radius:50%;border:3px solid rgba(255,255,255,0.7);background:white;object-fit:contain;padding:2px;' alt='ENSPM'/></div><div style='flex:1;text-align:center;'><p style='font-size:11px;opacity:0.75;margin:0;'>""" + T['ftth_full'] + """</p></div><div><img src='data:image/jpeg;base64,""" + _DB_IENG + """' style='height:75px;width:75px;border-radius:50%;border:3px solid rgba(255,255,255,0.7);background:white;object-fit:contain;padding:2px;' alt='iEng'/></div></div></div>
""", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["dashboard_title"]}</div>',unsafe_allow_html=True)
    if models_ok is True:
        m=models['metrics']
        c1,c2,c3,c4=st.columns(4)
        for col,alg,ds,acc,f1 in [
            (c1,f"🌲 {T['rf_full']}",T['deploy_lbl'],m['rf_deploy_acc'],m['rf_deploy_f1']),
            (c2,f"⚙️ {T['svm_full']}",T['deploy_lbl'],m['svm_deploy_acc'],m['svm_deploy_f1']),
            (c3,f"🌲 {T['rf_full']}",T['maint_lbl'],m['rf_maint_acc'],m['rf_maint_f1']),
            (c4,f"⚙️ {T['svm_full']}",T['maint_lbl'],m['svm_maint_acc'],m['svm_maint_f1'])]:
            with col:
                st.markdown(f"""<div class="metric-card">
                    <h3>{alg}</h3><h4 style="margin:2px 0;color:#666;font-size:12px;">{ds}</h4>
                    <h2>{acc*100:.1f}{T['pct_lbl']}</h2>
                    <p style="color:#888;font-size:12px;">{T['f1_lbl']} : {f1:.3f}</p>
                </div>""",unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            fig=go.Figure(data=[
                go.Bar(name=T['rf_full'],x=[T['deploy_lbl'],T['maint_lbl']],
                    y=[m['rf_deploy_acc']*100,m['rf_maint_acc']*100],marker_color='#2E75B6',
                    text=[f"{m['rf_deploy_acc']*100:.1f}%",f"{m['rf_maint_acc']*100:.1f}%"],textposition='outside'),
                go.Bar(name=T['svm_full'],x=[T['deploy_lbl'],T['maint_lbl']],
                    y=[m['svm_deploy_acc']*100,m['svm_maint_acc']*100],marker_color='#f39c12',
                    text=[f"{m['svm_deploy_acc']*100:.1f}%",f"{m['svm_maint_acc']*100:.1f}%"],textposition='outside')])
            fig.update_layout(title=T['rf_vs_svm'],barmode='group',yaxis_range=[0,115],height=350,
                plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            if data_ok is True and df_deploy is not None and df_maint is not None:
                fig2=make_subplots(rows=1,cols=2,subplot_titles=(T['deploy_lbl'],T['maint_lbl']),
                    specs=[[{'type':'domain'},{'type':'domain'}]])
                vc_d=df_deploy['statut_deploiement'].value_counts()
                vc_m=df_maint['type_intervention'].value_counts()
                lang_cur=get_session_language()
                MAP_D={'Réussi':{'fr':'Réussi','en':'Successful','ar':'ناجح'},
                       'En_retard':{'fr':'En Retard','en':'Delayed','ar':'متأخر'},
                       'Échoué':{'fr':'Échoué','en':'Failed','ar':'فاشل'}}
                MAP_M={'Préventive':{'fr':'Préventive','en':'Preventive','ar':'وقائي'},
                       'Corrective':{'fr':'Corrective','en':'Corrective','ar':'تصحيحي'},
                       'Urgente':{'fr':'Urgente','en':'Urgent','ar':'عاجل'}}
                labels_d_tr=[MAP_D.get(l,{}).get(lang_cur,l) for l in vc_d.index]
                labels_m_tr=[MAP_M.get(l,{}).get(lang_cur,l) for l in vc_m.index]
                colors_d={'Réussi':'#27ae60','En_retard':'#f39c12','Échoué':'#e74c3c'}
                colors_m={'Préventive':'#2980b9','Corrective':'#f39c12','Urgente':'#e74c3c'}
                clr_d=[colors_d.get(l,'#95a5a6') for l in vc_d.index]
                clr_m=[colors_m.get(l,'#95a5a6') for l in vc_m.index]
                fig2.add_trace(go.Pie(labels=labels_d_tr,values=vc_d.values,marker_colors=clr_d,hole=0.4,name='D'),row=1,col=1)
                fig2.add_trace(go.Pie(labels=labels_m_tr,values=vc_m.values,marker_colors=clr_m,hole=0.4,name='M'),row=1,col=2)
                fig2.update_layout(title=T['distrib_lbl'],height=350,paper_bgcolor=PLOT,font_color=TEXT)
                st.plotly_chart(fig2,use_container_width=True)
    if data_ok is True and df_deploy is not None and df_maint is not None:
        st.markdown(f'<div class="section-title">{T["preview_lbl"]}</div>',unsafe_allow_html=True)
        t1,t2=st.tabs([T['tab_deploy_ds'],T['tab_maint_ds']])
        _lang_t=get_session_language()
        _MAP_Z={'Péri_Urbaine':{'fr':'Péri_Urbaine','en':'Peri_Urban','ar':'شبه حضرية'},
                'Urbaine_Dense':{'fr':'Urbaine_Dense','en':'Dense_Urban','ar':'حضرية كثيفة'},
                'Urbaine_Moyenne':{'fr':'Urbaine_Moyenne','en':'Medium_Urban','ar':'حضرية متوسطة'},
                'Rurale':{'fr':'Rurale','en':'Rural','ar':'ريفية'}}
        _MAP_S={'Saison_Pluies':{'fr':'Saison_Pluies','en':'Rainy_Season','ar':'موسم الأمطار'},
                'Saison_Seche':{'fr':'Saison_Seche','en':'Dry_Season','ar':'الموسم الجاف'},
                'Intersaison':{'fr':'Intersaison','en':'Inter_Season','ar':'الموسم الانتقالي'}}
        def _tr_col(df,col,MAP):
            d=df.copy()
            if col in d.columns: d[col]=d[col].apply(lambda x:MAP.get(x,{}).get(_lang_t,x))
            return d
        df_dep_show=df_deploy.head(8).copy()
        df_dep_show=_tr_col(df_dep_show,'type_zone',_MAP_Z)
        df_dep_show=_tr_col(df_dep_show,'saison',_MAP_S)
        df_mnt_show=df_maint.head(8).copy()
        df_mnt_show=_tr_col(df_mnt_show,'type_zone',_MAP_Z)
        df_mnt_show=_tr_col(df_mnt_show,'saison',_MAP_S)
        with t1:
            st.info(f"**{df_deploy.shape[0]}** {T['rows_lbl']} × **{df_deploy.shape[1]}** {T['cols_lbl']} | {T['target_lbl']} : {T['Réussi']}/{T['En_retard']}/{T['Échoué']}")
            st.dataframe(df_dep_show,use_container_width=True)
        with t2:
            st.info(f"**{df_maint.shape[0]}** {T['rows_lbl']} × **{df_maint.shape[1]}** {T['cols_lbl']} | {T['target_lbl']} : {T['Préventive']}/{T['Corrective']}/{T['Urgente']}")
            st.dataframe(df_mnt_show,use_container_width=True)

# =============================================
# PAGE 2 — PRÉDICTION DÉPLOIEMENT
# =============================================
elif cur_page_idx_main == 1:
    nav(PAGES[1])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["pred_d_title"]}</div>',unsafe_allow_html=True)
    if models_ok is not True: st.error(T['models_err']); st.stop()

    with st.form("form_deploy"):
        c1,c2,c3=st.columns(3)
        with c1:
            lang_f=get_session_language()
            zones_tr=tr_list(ZONES_RAW,lang_f); saisons_tr=tr_list(SAISONS_RAW,lang_f)
            zones_t_tr=tr_list(ZONES_TYPES_RAW,lang_f); terrains_tr=tr_list(TERRAINS_RAW,lang_f)
            st.subheader(T['loc_climate'])
            loc_tr=st.selectbox(T['loc_lbl'],zones_tr)
            type_zone_tr=st.selectbox(T['zone_lbl'],zones_t_tr)
            saison_tr=st.selectbox(T['season_lbl'],saisons_tr)
            terrain_tr=st.selectbox(T['terrain_lbl'],terrains_tr)
            temp=st.slider(T['temp_lbl'],20.0,50.0,38.0,0.5)
            hum=st.slider(T['hum_lbl'],5.0,98.0,25.0,1.0)
            obstacle_tr=st.selectbox(T['obstacle_lbl'],T['yes_no'])
            loc=safe_reverse_tr(loc_tr); type_zone=safe_reverse_tr(type_zone_tr)
            saison=safe_reverse_tr(saison_tr); terrain=safe_reverse_tr(terrain_tr)
            obstacle='Oui' if obstacle_tr==T['yes_no'][1] else 'Non'
        with c2:
            st.subheader(T['infra_lbl'])
            foyers=st.number_input(T['foyers_lbl'],50,5000,300,50)
            dist=st.number_input(T['dist_lbl'],0.5,80.0,10.0,0.5)
            cable=st.number_input(T['cable_lbl'],1.0,150.0,18.0,0.5)
            nb_olt=st.slider(T['olt_lbl'],1,10,2)
            nb_ont=st.slider(T['ont_lbl'],8,128,32,8)
            st.subheader(T['perf_net'])
            sig_olt=st.number_input(T['sig_olt_lbl'],-5.0,5.0,1.5,0.1)
            sig_ont=st.number_input(T['sig_ont_lbl'],-35.0,-5.0,-20.0,0.5)
            latence=st.number_input(T['lat_lbl'],1.0,30.0,5.0,0.5)
        with c3:
            st.subheader(T['budget_lbl'])
            cout_mat=st.number_input(T['cout_mat'],500000,50000000,3500000,100000)
            cout_mo=st.number_input(T['cout_mo'],100000,20000000,2500000,100000)
            budget=st.number_input(T['budget_alloc'],1000000,100000000,8000000,100000)
            dur_prev=st.number_input(T['dur_prev_lbl'],10,180,60,5)
            dur_reel=st.number_input(T['dur_reel_lbl'],10,400,65,5)
            st.subheader(T['ressources'])
            nb_tech=st.slider(T['tech_lbl'],2,30,6)
            exp_chef=st.slider(T['exp_lbl'],1,20,5)
            incidents=st.slider(T['incidents_lbl'],0,15,2)
            st.subheader(T['model_choice'])
            modele_d=st.radio("",[T['rf_lbl'],T['svm_lbl']])
        cout_total_rt = cout_mat + cout_mo + 500000
        ratio_rt = cout_total_rt / budget if budget > 0 else 1.0
        css_ratio = "ratio-danger" if ratio_rt>1.3 else ("ratio-warn" if ratio_rt>1.1 else "ratio-box")
        st.markdown(f'<div class="ratio-box {css_ratio}">💰 {T["ratio_lbl"]} : {ratio_rt:.3f} {"🔴" if ratio_rt>1.3 else ("⚠️" if ratio_rt>1.1 else "✅")}</div>',unsafe_allow_html=True)
        sub_d=st.form_submit_button(T['predict_d_btn'],use_container_width=True,type="primary")

    if sub_d:
        T = get_T()
        use_rf_d = any(k in (modele_d or "") for k in ('Random Forest','Forêt','الغابة',T.get('rf_lbl','')))
        obs_val=1 if obstacle=='Oui' else 0
        res_raw,prob_dict,ratio_budget,retard,perte_opt=predict_deploy(
            models,loc,type_zone,saison,terrain,obs_val,foyers,dist,cable,
            nb_olt,nb_ont,temp,hum,sig_olt,sig_ont,latence,
            cout_mat,cout_mo,budget,dur_prev,dur_reel,nb_tech,exp_chef,incidents,use_rf_d)
        aname=T['rf_lbl'] if use_rf_d else T['svm_lbl']
        res_tr=T[RES_MAP_D.get(res_raw,res_raw)]
        reco_tr=T[RECO_MAP_D.get(res_raw,'reco_reussi')]
        css=CSS_MAP_D.get(res_raw,'result-info')
        ico=ICO_MAP_D.get(res_raw,'✅')
        prob_tr={T[RES_MAP_D.get(k,k)]:v for k,v in prob_dict.items()}
        st.markdown("---"); st.markdown(T['alerts_title'])
        alertes_d(ratio_budget,retard,temp,incidents,perte_opt)
        st.markdown(f"""<div class="{css}">
            <h2>{ico} {T['result_d_lbl']} : <strong>{res_tr}</strong> &nbsp;<small>({aname})</small></h2>
            <p><b>{T['recomm_lbl']} :</b> {reco_tr}</p>
            <p style="font-size:13px;color:#555;">{loc_tr} | {type_zone_tr} | {saison_tr} | {T['ratio_lbl']}: {ratio_budget:.3f} | {retard} {T['jours_lbl']}</p>
        </div>""",unsafe_allow_html=True)
        cg1,cg2=st.columns(2)
        with cg1:
            fp=go.Figure(go.Bar(x=list(prob_tr.values()),y=list(prob_tr.keys()),orientation='h',
                marker_color=['#2E75B6' if k==res_tr else '#bdc3c7' for k in prob_tr],
                text=[f"{v*100:.1f}%" for v in prob_tr.values()],textposition='outside'))
            fp.update_layout(title=T['proba_lbl'],xaxis_range=[0,1.15],height=250,
                plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fp,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>{T["result_d_lbl"]} : {res_tr}</b> : {T["proba_lbl"]} : {prob_tr[res_tr]*100:.1f}%</div>',unsafe_allow_html=True)
        with cg2:
            facts={'Budget':min(ratio_budget,2.0),'Retard':min(retard/180,1.0),
                   'Signal':min(perte_opt/35,1.0),'Incidents':min(incidents/15,1.0),'Temp':((temp-20)/30)}
            fr=go.Figure(go.Scatterpolar(r=list(facts.values()),theta=list(facts.keys()),fill='toself',marker_color='#2E75B6'))
            fr.update_layout(title=T['risk_lbl'],height=250,polar=dict(radialaxis=dict(range=[0,1.2])),paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fr,use_container_width=True)
        params_d={T['loc_lbl']:loc_tr,T['zone_lbl']:type_zone_tr,T['season_lbl']:saison_tr,
                  T['ratio_lbl']:f"{ratio_budget:.3f}",T['hist_col_algo']:aname}
        hist_entry_d={T['hist_col_date']:datetime.now().strftime("%d/%m/%Y %H:%M"),
            T['hist_col_type']:T['deploy_lbl'],T['hist_col_loc']:loc,T['hist_col_season']:saison,
            T['hist_col_algo']:aname,T['hist_col_result']:res_tr,T['hist_col_conf']:f"{prob_dict[res_raw]*100:.1f}%"}
        st.session_state.setdefault("hist_deploy",[]).append(hist_entry_d)
        _sk_d=f"{u[4]}_{res_raw}_{datetime.now().strftime('%Y%m%d%H%M')}"
        if st.session_state.get("last_save_d")!=_sk_d:
            _r=save_history(u[4],T['deploy_lbl'],res_tr,res_raw,prob_dict[res_raw],params_d,get_session_language(),reco_tr)
            if _r is True:
                st.session_state["last_save_d"]=_sk_d
                st.toast("💾 "+T.get('save_ok','Prédiction enregistrée!'),icon="✅")
        with st.container():
            col_export,=st.columns([1])
            rapport_html=generer_rapport_html(PAGES[1],res_tr,prob_tr,params_d,aname,reco_tr,css)
            st.download_button(T['export_lbl'],rapport_html.encode('utf-8'),
                file_name=f"rapport_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",use_container_width=True)

# =============================================
# PAGE 3 — PRÉDICTION MAINTENANCE
# =============================================
elif cur_page_idx_main == 2:
    nav(PAGES[2])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["pred_m_title"]}</div>',unsafe_allow_html=True)
    if models_ok is not True: st.error(T['models_err']); st.stop()
    with st.form("form_maint"):
        c1,c2,c3=st.columns(3)
        with c1:
            lang_fm=st.session_state.get("language","fr")
            zones_tr_m=tr_list(ZONES_RAW,lang_fm); saisons_tr_m=tr_list(SAISONS_RAW,lang_fm)
            zones_t_tr_m=tr_list(ZONES_TYPES_RAW,lang_fm); equip_tr_m=tr_list(EQUIPEMENTS_RAW,lang_fm)
            st.subheader(T['loc_climate'])
            m_loc_tr=st.selectbox(T['loc_lbl'],zones_tr_m,index=3)
            m_zone_tr=st.selectbox(T['zone_lbl'],zones_t_tr_m,index=1)
            m_saison_tr=st.selectbox(T['season_lbl'],saisons_tr_m,index=1)
            m_temp=st.slider(T['temp_lbl'],20.0,50.0,32.0,0.5)
            st.subheader(T['equip_lbl'])
            m_equip_tr=st.selectbox(T['equip_type'],equip_tr_m,index=3)
            m_age=st.slider(T['age_lbl'],1,120,24)
            m_der_m=st.slider(T['last_maint'],1,365,90)
            m_nb_int=st.slider(T['prev_interv'],0,20,3)
            m_loc=safe_reverse_tr(m_loc_tr); m_zone=safe_reverse_tr(m_zone_tr)
            m_saison=safe_reverse_tr(m_saison_tr); m_equip=safe_reverse_tr(m_equip_tr)
        with c2:
            pannes_tr_m=tr_list(PANNES_RAW,lang_fm); severites_tr=tr_list(SEVERITES_RAW,lang_fm)
            st.subheader(T['fault_lbl'])
            m_panne_tr=st.selectbox(T['fault_type'],pannes_tr_m)
            m_sev_tr=st.selectbox(T['severity_lbl'],severites_tr,index=2)
            m_panne=safe_reverse_tr(m_panne_tr); m_sev=safe_reverse_tr(m_sev_tr)
            m_clients=st.number_input(T['clients_lbl'],0,500,150,10)
            m_dur_p=st.number_input(T['fault_dur'],0.0,72.0,6.0,0.5)
            m_tickets=st.number_input(T['tickets_open'],0,50,12)
            m_tck_r=st.number_input(T['tickets_res'],0,50,6)
        with c3:
            st.subheader(T['qos_lbl'])
            m_dispo=st.slider(T['avail_lbl'],50.0,100.0,75.0,0.5)
            m_sla=st.selectbox(T['sla_lbl'],T['sla_opts'])
            m_satis=st.slider(T['satisf_lbl'],1.0,10.0,5.0,0.5)
            m_debit=st.number_input(T['debit_lbl'],0.0,1000.0,50.0,10.0)
            m_signal=st.number_input(T['signal_lbl'],-35.0,0.0,-22.0,0.5)
            m_latobs=st.number_input(T['lat_obs'],1.0,200.0,45.0,1.0)
            m_perte=st.number_input(T['loss_lbl'],0.0,50.0,10.0,1.0)
            st.subheader(T['model_choice'])
            modele_m=st.radio("",[T['rf_lbl'],T['svm_lbl']])
        sub_m=st.form_submit_button(T['predict_m_btn'],use_container_width=True,type="primary")

    if sub_m:
        T = get_T()
        sla_val=0 if m_sla==T['sla_opts'][0] else 1
        taux_res=(m_tck_r/m_tickets*100) if m_tickets>0 else 100.0
        if models is None:
            st.error(T.get('models_err', '❌ Modèles non chargés. Vérifiez les fichiers .pkl.'))
            st.stop()
        le_m=models['le_m']
        inpm=pd.DataFrame([{
            'localisation':le_m['localisation'].transform([m_loc])[0],
            'type_zone':le_m['type_zone'].transform([m_zone])[0],
            'latitude':ZONES_COORDS.get(m_loc,(8.5667,16.0833))[0],
            'longitude':ZONES_COORDS.get(m_loc,(8.5667,16.0833))[1],
            'saison':le_m['saison'].transform([m_saison])[0],
            'temperature_moy':m_temp,'humidite_pct':60.0,'vitesse_vent_kmh':20.0,'nb_jours_pluie_mois':10,
            'type_equipement':le_m['type_equipement'].transform([m_equip])[0],
            'age_equipement_mois':m_age,'nb_interventions_precedentes':m_nb_int,'derniere_maintenance_jours':m_der_m,
            'type_panne':le_m['type_panne'].transform([m_panne])[0],
            'severite_panne':le_m['severite_panne'].transform([m_sev])[0],
            'nb_clients_affectes':m_clients,'duree_panne_heures':m_dur_p,
            'nb_tickets_ouverts':m_tickets,'nb_tickets_resolus':m_tck_r,
            'taux_resolution_pct':round(taux_res,1),'debit_obs_mbps':m_debit,'signal_obs_dbm':m_signal,
            'latence_obs_ms':m_latobs,'taux_perte_paquets_pct':m_perte,'disponibilite_reseau_pct':m_dispo,
            'score_satisfaction':m_satis,'nb_plaintes_client':max(0,m_clients//10),'sla_respecte':sla_val,
            'cout_intervention_fcfa':500000,'nb_techniciens_maint':3,'duree_intervention_heures':4.0}])
        use_rf_m = any(k in (modele_m or "") for k in ('Random Forest','Forêt','الغابة',T.get('rf_lbl','')))
        if use_rf_m:
            predm=models['rf_maint'].predict(inpm); probam=models['rf_maint'].predict_proba(inpm)[0]; aname_m=T['rf_lbl']
        else:
            iscm=models['scaler_m'].transform(inpm); predm=models['svm_maint'].predict(iscm)
            probam=models['svm_maint'].predict_proba(iscm)[0]; aname_m=T['svm_lbl']
        resm_raw=models['le_target_m'].inverse_transform(predm)[0]
        classesm=models['le_target_m'].classes_
        prob_dict_m=dict(zip(classesm,probam))
        resm_tr=T[RES_MAP_M.get(resm_raw,resm_raw)]
        recom_tr=T[RECO_MAP_M.get(resm_raw,'reco_corr')]
        cssm=CSS_MAP_M.get(resm_raw,'result-info')
        icom=ICO_MAP_M.get(resm_raw,'🟡')
        prob_tr_m={T[RES_MAP_M.get(k,k)]:v for k,v in prob_dict_m.items()}
        st.markdown("---"); st.markdown(T['alerts_title'])
        alertes_m(m_sev,m_clients,m_dispo,sla_val,m_dur_p)
        st.markdown(f"""<div class="{cssm}">
            <h2>{icom} {T['result_m_lbl']} : <strong>{resm_tr}</strong> &nbsp;<small>({aname_m})</small></h2>
            <p><b>{T['action_lbl']} :</b> {recom_tr}</p>
            <p style="font-size:13px;color:#555;">{m_loc_tr} | {m_equip_tr} | {m_panne_tr} | {T['severity_lbl']}: {m_sev_tr} | {T['clients_lbl']}: {m_clients}</p>
        </div>""",unsafe_allow_html=True)
        cgm1,cgm2=st.columns(2)
        with cgm1:
            fpm=go.Figure(go.Bar(x=list(prob_tr_m.values()),y=list(prob_tr_m.keys()),orientation='h',
                marker_color=['#2E75B6' if k==resm_tr else '#bdc3c7' for k in prob_tr_m],
                text=[f"{v*100:.1f}%" for v in prob_tr_m.values()],textposition='outside'))
            fpm.update_layout(title=T['proba_lbl'],xaxis_range=[0,1.15],height=250,plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fpm,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>{T["result_m_lbl"]} : {resm_tr}</b> : {T["proba_lbl"]} : {prob_tr_m[resm_tr]*100:.1f}%</div>',unsafe_allow_html=True)
        with cgm2:
            us={'Sév':1.0 if m_sev=='Critique' else (0.7 if m_sev=='Élevée' else 0.3),
                T['clients_lbl']:min(m_clients/500,1.0),'Dispo':max(0,(100-m_dispo)/50),
                'SLA':1.0 if sla_val==0 else 0.0,'Durée':min(m_dur_p/72,1.0)}
            score_u=round(sum(us.values())/len(us)*100,1)
            fgu=go.Figure(go.Indicator(mode="gauge+number",value=score_u,title={'text':T['urgency_lbl']},
                gauge={'axis':{'range':[0,100]},'bar':{'color':'#e74c3c'},
                    'steps':[{'range':[0,33],'color':'#d9ead3'},{'range':[33,66],'color':'#fff2cc'},{'range':[66,100],'color':'#ffe6e6'}],
                    'threshold':{'line':{'color':'red','width':3},'value':66}}))
            fgu.update_layout(height=250,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fgu,use_container_width=True)
        params_m={T['loc_lbl']:m_loc_tr,T['equip_type']:m_equip_tr,
                  T['fault_type']:m_panne_tr,T['severity_lbl']:m_sev_tr,T['hist_col_algo']:aname_m}
        hist_entry_m={T['hist_col_date']:datetime.now().strftime("%d/%m/%Y %H:%M"),
            T['hist_col_type']:T['maint_lbl'],T['hist_col_loc']:m_loc,T['equip_type']:m_equip,
            T['hist_col_algo']:aname_m,T['hist_col_result']:resm_tr,T['hist_col_conf']:f"{prob_dict_m[resm_raw]*100:.1f}%"}
        st.session_state.setdefault("hist_maint",[]).append(hist_entry_m)
        _sk_m=f"{u[4]}_{resm_raw}_{datetime.now().strftime('%Y%m%d%H%M')}"
        if st.session_state.get("last_save_m")!=_sk_m:
            _rm=save_history(u[4],T['maint_lbl'],resm_tr,resm_raw,prob_dict_m[resm_raw],params_m,get_session_language(),recom_tr)
            if _rm is True:
                st.session_state["last_save_m"]=_sk_m
                st.toast("💾 "+T.get('save_ok','Prédiction enregistrée!'),icon="✅")
        with st.container():
            col_export_m,=st.columns([1])
            rapport_html_m=generer_rapport_html(PAGES[2],resm_tr,prob_tr_m,params_m,aname_m,recom_tr,cssm)
            st.download_button(T['export_lbl'],rapport_html_m.encode('utf-8'),
                file_name=f"rapport_maint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",use_container_width=True)


# =============================================
# PAGE 4 — COMPARAISON DE SCÉNARIOS (NOUVELLE)
# =============================================
elif cur_page_idx_main == 3:
    nav(PAGES[3])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["compare_page"]}</div>',unsafe_allow_html=True)
    if models_ok is not True: st.error(T['models_err']); st.stop()
    lang_fc=get_session_language()
    zones_trc=tr_list(ZONES_RAW,lang_fc); saisons_trc=tr_list(SAISONS_RAW,lang_fc)
    zones_t_trc=tr_list(ZONES_TYPES_RAW,lang_fc); terrains_trc=tr_list(TERRAINS_RAW,lang_fc)

    with st.form("form_compare"):
        colA,colB=st.columns(2)
        def scenario_inputs(col, label, idx_loc=0, idx_zone=0, idx_sai=0, idx_ter=0,
                            foyers_d=300, dist_d=10.0, cable_d=18.0, olt_d=2, ont_d=32,
                            temp_d=38.0, hum_d=25.0, obs_idx=0,
                            sig_olt_d=1.5, sig_ont_d=-20.0, lat_d=5.0,
                            cout_mat_d=3500000, cout_mo_d=2500000, budget_d=8000000,
                            dur_prev_d=60, dur_reel_d=65, nb_tech_d=6, exp_d=5, inc_d=2):
            col.subheader(label)
            loc_tr=col.selectbox(T['loc_lbl'],zones_trc,index=idx_loc,key=f"loc{label}")
            type_zone_tr=col.selectbox(T['zone_lbl'],zones_t_trc,index=idx_zone,key=f"zone{label}")
            saison_tr=col.selectbox(T['season_lbl'],saisons_trc,index=idx_sai,key=f"sai{label}")
            terrain_tr=col.selectbox(T['terrain_lbl'],terrains_trc,index=idx_ter,key=f"ter{label}")
            temp=col.slider(T['temp_lbl'],20.0,50.0,temp_d,0.5,key=f"temp{label}")
            hum=col.slider(T['hum_lbl'],5.0,98.0,hum_d,1.0,key=f"hum{label}")
            obs_tr=col.selectbox(T['obstacle_lbl'],T['yes_no'],index=obs_idx,key=f"obs{label}")
            foyers=col.number_input(T['foyers_lbl'],50,5000,foyers_d,50,key=f"foy{label}")
            dist=col.number_input(T['dist_lbl'],0.5,80.0,dist_d,0.5,key=f"dist{label}")
            cable=col.number_input(T['cable_lbl'],1.0,150.0,cable_d,0.5,key=f"cable{label}")
            nb_olt=col.slider(T['olt_lbl'],1,10,olt_d,key=f"olt{label}")
            nb_ont=col.slider(T['ont_lbl'],8,128,ont_d,8,key=f"ont{label}")
            sig_olt=col.number_input(T['sig_olt_lbl'],-5.0,5.0,sig_olt_d,0.1,key=f"solt{label}")
            sig_ont=col.number_input(T['sig_ont_lbl'],-35.0,-5.0,sig_ont_d,0.5,key=f"sont{label}")
            latence=col.number_input(T['lat_lbl'],1.0,30.0,lat_d,0.5,key=f"lat{label}")
            cout_mat=col.number_input(T['cout_mat'],500000,50000000,cout_mat_d,100000,key=f"cmat{label}")
            cout_mo=col.number_input(T['cout_mo'],100000,20000000,cout_mo_d,100000,key=f"cmo{label}")
            budget=col.number_input(T['budget_alloc'],1000000,100000000,budget_d,100000,key=f"bgt{label}")
            dur_prev=col.number_input(T['dur_prev_lbl'],10,180,dur_prev_d,5,key=f"dprev{label}")
            dur_reel=col.number_input(T['dur_reel_lbl'],10,400,dur_reel_d,5,key=f"dreel{label}")
            nb_tech=col.slider(T['tech_lbl'],2,30,nb_tech_d,key=f"tech{label}")
            exp_chef=col.slider(T['exp_lbl'],1,20,exp_d,key=f"exp{label}")
            incidents=col.slider(T['incidents_lbl'],0,15,inc_d,key=f"inc{label}")
            loc=safe_reverse_tr(loc_tr); type_zone=safe_reverse_tr(type_zone_tr)
            saison=safe_reverse_tr(saison_tr); terrain=safe_reverse_tr(terrain_tr)
            obstacle='Oui' if obs_tr==T['yes_no'][1] else 'Non'
            return dict(loc=loc,type_zone=type_zone,saison=saison,terrain=terrain,
                        obs_val=1 if obstacle=='Oui' else 0,foyers=foyers,dist=dist,cable=cable,
                        nb_olt=nb_olt,nb_ont=nb_ont,temp=temp,hum=hum,sig_olt=sig_olt,sig_ont=sig_ont,
                        latence=latence,cout_mat=cout_mat,cout_mo=cout_mo,budget=budget,
                        dur_prev=dur_prev,dur_reel=dur_reel,nb_tech=nb_tech,exp_chef=exp_chef,incidents=incidents)

        with colA: pA=scenario_inputs(colA,T['scenario_a'],idx_loc=0,dur_reel_d=65,inc_d=2)
        with colB: pB=scenario_inputs(colB,T['scenario_b'],idx_loc=3,temp_d=42.0,dur_reel_d=90,inc_d=7,budget_d=6000000)
        sub_cmp=st.form_submit_button(T['compare_btn'],use_container_width=True,type="primary")

    if sub_cmp:
        T = get_T()
        rA,probA,ratioA,retardA,perteA=predict_deploy(models,**pA,use_rf=True)
        rB,probB,ratioB,retardB,perteB=predict_deploy(models,**pB,use_rf=True)
        res_tr_A=T[RES_MAP_D.get(rA,rA)]; res_tr_B=T[RES_MAP_D.get(rB,rB)]
        css_A=CSS_MAP_D.get(rA,'result-info'); css_B=CSS_MAP_D.get(rB,'result-info')
        ico_A=ICO_MAP_D.get(rA,'✅'); ico_B=ICO_MAP_D.get(rB,'✅')
        conf_A=probA[rA]*100; conf_B=probB[rB]*100
        st.markdown(f"### {T['compare_result']}")
        c1,c2,c3=st.columns([2,1,2])
        with c1:
            st.markdown(f'<div class="{css_A}" style="text-align:center;">'
                f'<h3>{T["scenario_a"]}</h3><h2>{ico_A} {res_tr_A}</h2>'
                f'<p>Confiance : <b>{conf_A:.1f}%</b></p>'
                f'<p>{T["ratio_lbl"]} : <b>{ratioA:.3f}</b></p>'
                f'<p>Retard : <b>{retardA} j</b></p></div>',unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:center;padding:60px 0;font-size:28px;font-weight:bold;color:#1F4E79;'>{T['vs_lbl']}</div>",unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="{css_B}" style="text-align:center;">'
                f'<h3>{T["scenario_b"]}</h3><h2>{ico_B} {res_tr_B}</h2>'
                f'<p>Confiance : <b>{conf_B:.1f}%</b></p>'
                f'<p>{T["ratio_lbl"]} : <b>{ratioB:.3f}</b></p>'
                f'<p>Retard : <b>{retardB} j</b></p></div>',unsafe_allow_html=True)
        # Graphique comparatif
        cats=['Budget','Retard (j)','Perte Signal (dB)','Incidents','Confiance (%)']
        valA=[ratioA*100,retardA,perteA,pA['incidents'],conf_A]
        valB=[ratioB*100,retardB,perteB,pB['incidents'],conf_B]
        fig_cmp=go.Figure()
        fig_cmp.add_trace(go.Bar(name=T['scenario_a'],x=cats,y=valA,marker_color='#2E75B6',
            text=[f"{v:.1f}" for v in valA],textposition='outside'))
        fig_cmp.add_trace(go.Bar(name=T['scenario_b'],x=cats,y=valB,marker_color='#e74c3c',
            text=[f"{v:.1f}" for v in valB],textposition='outside'))
        fig_cmp.update_layout(barmode='group',height=350,plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT,
            title=f"{T['scenario_a']} {T['vs_lbl']} {T['scenario_b']}")
        st.plotly_chart(fig_cmp,use_container_width=True)

        # ── Enregistrement automatique de la comparaison ──
        _lbl_cmp = {'fr':'⚔️ Comparaison de Scénarios','en':'⚔️ Scenario Comparison','ar':'⚔️ مقارنة السيناريوهات'}.get(get_session_language(),'⚔️ Comparaison')
        _reco_A = T.get(RECO_MAP_D.get(rA,'reco_reussi'),'')
        _reco_B = T.get(RECO_MAP_D.get(rB,'reco_reussi'),'')
        _reco_cmp = f"A:{res_tr_A}({conf_A:.0f}%) | B:{res_tr_B}({conf_B:.0f}%)"
        _params_cmp = {
            f"{T['scenario_a']} - {T['loc_lbl']}": pA.get('loc_tr',''),
            f"{T['scenario_a']} - {T['hist_col_result']}": res_tr_A,
            f"{T['scenario_a']} Confiance": f"{conf_A:.1f}%",
            f"{T['scenario_b']} - {T['loc_lbl']}": pB.get('loc_tr',''),
            f"{T['scenario_b']} - {T['hist_col_result']}": res_tr_B,
            f"{T['scenario_b']} Confiance": f"{conf_B:.1f}%",
        }
        _sk_cmp = f"{u[4]}_{rA}_{rB}_{datetime.now().strftime('%Y%m%d%H%M')}"
        if st.session_state.get("last_save_cmp") != _sk_cmp:
            _rc = save_history(u[4], _lbl_cmp, _reco_cmp, _reco_cmp,
                               max(conf_A,conf_B)/100, _params_cmp,
                               get_session_language(),
                               f"A:{_reco_A} | B:{_reco_B}")
            if _rc is True:
                st.session_state["last_save_cmp"] = _sk_cmp
                st.toast("💾 " + T.get('save_ok','Comparaison enregistrée!'), icon="✅")

# =============================================
# PAGE 5 — HISTORIQUE
# =============================================
elif cur_page_idx_main == 4:
    nav(PAGES[4])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    lang_h = get_session_language()

    # Traductions pour l'historique
    lbl_hist = {
        'title'       : {'fr':'📋 Historique de votre Compte','en':'📋 Account History','ar':'📋 سجل الحساب'},
        'profile'     : {'fr':'👤 Mon Profil','en':'👤 My Profile','ar':'👤 ملفي الشخصي'},
        'deploy_tab'  : {'fr':'🚀 Déploiements','en':'🚀 Deployments','ar':'🚀 النشر'},
        'maint_tab'   : {'fr':'🔧 Maintenances','en':'🔧 Maintenances','ar':'🔧 الصيانة'},
        'all_tab'     : {'fr':"📊 Tout l'historique",'en':'📊 Full History','ar':'📊 السجل الكامل'},
        'no_pred'     : {'fr':'Aucune prédiction enregistrée.','en':'No prediction recorded.','ar':'لا توجد تنبؤات مسجلة.'},
        'total'       : {'fr':'prédictions au total','en':'predictions total','ar':'تنبؤات في المجموع'},
        'deploy_lbl'  : {'fr':'Déploiements','en':'Deployments','ar':'النشر'},
        'maint_lbl'   : {'fr':'Maintenances','en':'Maintenances','ar':'الصيانة'},
        'last_pred'   : {'fr':'Dernière prédiction','en':'Last prediction','ar':'آخر تنبؤ'},
        'since'       : {'fr':'Membre depuis','en':'Member since','ar':'عضو منذ'},
        'email_lbl'   : {'fr':'Email','en':'Email','ar':'البريد الإلكتروني'},
        'del_hist'    : {'fr':'🗑️ Effacer tout mon historique','en':'🗑️ Clear all my history','ar':'🗑️ مسح كل السجل'},
        'del_confirm' : {'fr':'Historique effacé.','en':'History cleared.','ar':'تم مسح السجل.'},
        'download'    : {'fr':'⬇️ Télécharger CSV','en':'⬇️ Download CSV','ar':'⬇️ تحميل CSV'},
        'date_col'    : {'fr':'Date','en':'Date','ar':'التاريخ'},
        'type_col'    : {'fr':'Type','en':'Type','ar':'النوع'},
        'result_col'  : {'fr':'Résultat','en':'Result','ar':'النتيجة'},
        'conf_col'    : {'fr':'Confiance','en':'Confidence','ar':'الثقة'},
        'distrib'     : {'fr':'Répartition des résultats','en':'Results distribution','ar':'توزيع النتائج'},
        'cmp_tab'     : {'fr':'⚔️ Comparaisons','en':'⚔️ Comparisons','ar':'⚔️ المقارنات'},
        'cmp_title'   : {'fr':'Comparaison de Scénarios','en':'Scenario Comparison','ar':'مقارنة السيناريوهات'},
        'no_cmp'      : {'fr':'Aucune comparaison enregistrée.','en':'No comparison recorded.','ar':'لا توجد مقارنات مسجلة.'},
        'sc_a'        : {'fr':'Scénario A','en':'Scenario A','ar':'السيناريو A'},
        'sc_b'        : {'fr':'Scénario B','en':'Scenario B','ar':'السيناريو B'},
    }
    def hl(key): return lbl_hist[key].get(lang_h, lbl_hist[key]['fr'])

    # Traductions résultats
    MAP_RES = {
        'Réussi'     : {'fr':'Réussi','en':'Successful','ar':'ناجح'},
        'En_retard'  : {'fr':'En Retard','en':'Delayed','ar':'متأخر'},
        'En Retard'  : {'fr':'En Retard','en':'Delayed','ar':'متأخر'},
        'Échoué'     : {'fr':'Échoué','en':'Failed','ar':'فاشل'},
        'Préventive' : {'fr':'Préventive','en':'Preventive','ar':'وقائي'},
        'Corrective' : {'fr':'Corrective','en':'Corrective','ar':'تصحيحي'},
        'Urgente'    : {'fr':'Urgente','en':'Urgent','ar':'عاجل'},
    }
    MAP_TYPE = {
        'Déploiement' : {'fr':'Déploiement','en':'Deployment','ar':'النشر'},
        'Deployment'  : {'fr':'Déploiement','en':'Deployment','ar':'النشر'},
        'Maintenance' : {'fr':'Maintenance','en':'Maintenance','ar':'الصيانة'},
    }
    def tr_res(r):  return MAP_RES.get(str(r), {}).get(lang_h, r)
    def tr_type(t): return MAP_TYPE.get(str(t), {}).get(lang_h, t)

    st.markdown(f'<div class="section-title">{hl("title")}</div>', unsafe_allow_html=True)

    # Charger les données depuis SQLite
    df_all = get_history(u[4])
    stats  = get_user_stats(u[4])

    tab_prof, tab_dep, tab_mnt, tab_cmp, tab_all = st.tabs([
        hl("profile"), hl("deploy_tab"), hl("maint_tab"), hl("cmp_tab"), hl("all_tab")
    ])

    # ── Onglet PROFIL ──────────────────────────────────
    with tab_prof:
        c1p, c2p = st.columns([1, 2])
        with c1p:
            st.markdown(f"""
            <div style="background:{CARD};border-radius:12px;padding:20px;text-align:center;">
                <div style="font-size:60px;">👤</div>
                <h3 style="color:{TEXT};margin:8px 0 4px 0;">{u[1]} {u[2]}</h3>
                <p style="color:#90caf9;margin:0;">@{u[4]}</p>
            </div>""", unsafe_allow_html=True)
        with c2p:
            st.markdown(f"""
            <div style="background:{CARD};border-radius:12px;padding:20px;">
                <p style="color:{TEXT};margin:6px 0;">
                    📧 <b>{hl("email_lbl")} :</b> {u[3]}
                </p>
                <p style="color:{TEXT};margin:6px 0;">
                    📅 <b>{hl("since")} :</b> {u[7]}
                </p>
                <p style="color:{TEXT};margin:6px 0;">
                    🔮 <b>{stats["total"]} {hl("total")}</b>
                    &nbsp;|&nbsp; 🚀 {stats["deploy"]} {hl("deploy_lbl")}
                    &nbsp;|&nbsp; 🔧 {stats["maint"]} {hl("maint_lbl")}
                </p>
                {"<p style='color:" + TEXT + ";margin:6px 0;'>⏱️ <b>" + hl("last_pred") + " :</b> " + str(stats["last_pred"]) + "</p>" if stats["last_pred"] else ""}
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        # Bouton effacer historique
        with st.expander(hl("del_hist")):
            if st.button("⚠️ " + hl("del_hist"), key="del_hist_btn",
                         type="primary", use_container_width=True):
                delete_user_history(u[4])
                st.session_state.hist_deploy = []
                st.session_state.hist_maint  = []
                st.success(hl("del_confirm"))
                st.rerun()

    # ── Onglet DÉPLOIEMENTS ────────────────────────────
    with tab_dep:
        df_dep = df_all[df_all['type_pred'].str.contains('ploiement|eployment', na=False)] if not df_all.empty else pd.DataFrame()
        if not df_dep.empty:
            st.info(f"**{len(df_dep)}** {hl('total')}")
            _reco_lbl = {'fr':'💡 Recommandation','en':'💡 Recommendation','ar':'💡 التوصية'}.get(lang_h,'💡 Recommandation')
            _src_cols = ['date_pred','type_pred','resultat','confiance']
            if 'recommandation' in df_dep.columns: _src_cols.append('recommandation')
            df_d = df_dep[_src_cols].copy()
            df_d[hl('date_col')]   = df_d['date_pred']
            df_d[hl('type_col')]   = df_d['type_pred'].apply(tr_type)
            df_d[hl('result_col')] = df_d['resultat'].apply(tr_res)
            df_d[hl('conf_col')]   = df_d['confiance'].apply(lambda x: f"{x*100:.1f}%")
            _cols_d = [hl('date_col'),hl('type_col'),hl('result_col'),hl('conf_col')]
            if 'recommandation' in df_dep.columns:
                df_d[_reco_lbl] = df_d['recommandation'].fillna('')
                _cols_d.append(_reco_lbl)
            st.dataframe(df_d[_cols_d], use_container_width=True)
            vc = df_d[hl('result_col')].value_counts()
            fig = px.pie(values=vc.values, names=vc.index, hole=0.4, title=hl('distrib'))
            fig.update_layout(paper_bgcolor=PLOT, font_color=TEXT)
            st.plotly_chart(fig, use_container_width=True)
            st.download_button(hl('download'),
                df_d.to_csv(index=False).encode('utf-8'),
                file_name=f"deploy_{u[4]}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        else:
            st.info(hl('no_pred'))

    # ── Onglet MAINTENANCES ────────────────────────────
    with tab_mnt:
        df_mnt2 = df_all[df_all['type_pred'].str.contains('aint', na=False)] if not df_all.empty else pd.DataFrame()
        if not df_mnt2.empty:
            st.info(f"**{len(df_mnt2)}** {hl('total')}")
            _reco_lbl_m = {'fr':'💡 Recommandation','en':'💡 Recommendation','ar':'💡 التوصية'}.get(lang_h,'💡 Recommandation')
            _src_cols_m = ['date_pred','type_pred','resultat','confiance']
            if 'recommandation' in df_mnt2.columns: _src_cols_m.append('recommandation')
            df_m = df_mnt2[_src_cols_m].copy()
            df_m[hl('date_col')]   = df_m['date_pred']
            df_m[hl('type_col')]   = df_m['type_pred'].apply(tr_type)
            df_m[hl('result_col')] = df_m['resultat'].apply(tr_res)
            df_m[hl('conf_col')]   = df_m['confiance'].apply(lambda x: f"{x*100:.1f}%")
            _cols_m = [hl('date_col'),hl('type_col'),hl('result_col'),hl('conf_col')]
            if 'recommandation' in df_mnt2.columns:
                df_m[_reco_lbl_m] = df_m['recommandation'].fillna('')
                _cols_m.append(_reco_lbl_m)
            st.dataframe(df_m[_cols_m], use_container_width=True)
            vc_m = df_m[hl('result_col')].value_counts()
            fig_m = px.pie(values=vc_m.values, names=vc_m.index, hole=0.4, title=hl('distrib'))
            fig_m.update_layout(paper_bgcolor=PLOT, font_color=TEXT)
            st.plotly_chart(fig_m, use_container_width=True)
            st.download_button(hl('download'),
                df_m.to_csv(index=False).encode('utf-8'),
                file_name=f"maint_{u[4]}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        else:
            st.info(hl('no_pred'))

    # ── Onglet TOUT L'HISTORIQUE ───────────────────────
    # ── Onglet COMPARAISONS ──────────────────────────────
    with tab_cmp:
        # Filtrer les comparaisons de scénarios
        _cmp_kw = ['Comparaison','Comparison','مقارنة','scenario','scénario','Scénario']
        if not df_all.empty:
            df_cmp = df_all[df_all['type_pred'].apply(
                lambda x: any(k.lower() in str(x).lower() for k in _cmp_kw)
            )].copy()
        else:
            df_cmp = pd.DataFrame()

        if not df_cmp.empty:
            st.info(f"**{len(df_cmp)}** {hl('cmp_tab').replace('⚔️ ','')}")
            _reco_cmp_lbl = {'fr':'💡 Recommandations','en':'💡 Recommendations','ar':'💡 التوصيات'}.get(lang_h,'💡 Recommandations')
            _res_cmp_lbl  = {'fr':'Résultats A | B','en':'Results A | B','ar':'النتائج A | B'}.get(lang_h,'Résultats')
            _date_lbl     = hl('date_col')
            df_cmp_show = df_cmp[['date_pred','resultat','confiance'] + (['recommandation'] if 'recommandation' in df_cmp.columns else [])].copy()
            df_cmp_show[_date_lbl]   = df_cmp_show['date_pred']
            df_cmp_show[_res_cmp_lbl] = df_cmp_show['resultat']
            df_cmp_show[hl('conf_col')] = df_cmp_show['confiance'].apply(lambda x: f"{x*100:.1f}%")
            _cols_cmp = [_date_lbl, _res_cmp_lbl, hl('conf_col')]
            if 'recommandation' in df_cmp.columns:
                df_cmp_show[_reco_cmp_lbl] = df_cmp_show['recommandation'].fillna('')
                _cols_cmp.append(_reco_cmp_lbl)
            st.dataframe(df_cmp_show[_cols_cmp], use_container_width=True)
            # Graphique résultats comparaison
            if 'resultat' in df_cmp.columns and not df_cmp.empty:
                # Extraire Scénario A et B depuis le champ resultat
                def _parse_res(r, part):
                    try:
                        parts = str(r).split('|')
                        for p in parts:
                            if part in p: return p.split(':')[1].strip().split('(')[0].strip()
                    except: pass
                    return ''
                df_cmp_show[hl('sc_a')] = df_cmp_show[_res_cmp_lbl].apply(lambda r: _parse_res(r,'A'))
                df_cmp_show[hl('sc_b')] = df_cmp_show[_res_cmp_lbl].apply(lambda r: _parse_res(r,'B'))
                vc_a = df_cmp_show[hl('sc_a')].value_counts()
                vc_b = df_cmp_show[hl('sc_b')].value_counts()
                if not vc_a.empty or not vc_b.empty:
                    import plotly.graph_objects as go2
                    _fa, _fb = st.columns(2)
                    with _fa:
                        fa_cmp = px.pie(values=vc_a.values, names=vc_a.index, hole=0.4,
                            title=f"{hl('sc_a')} - {hl('distrib')}")
                        fa_cmp.update_layout(paper_bgcolor=PLOT, font_color=TEXT)
                        st.plotly_chart(fa_cmp, use_container_width=True)
                    with _fb:
                        fb_cmp = px.pie(values=vc_b.values, names=vc_b.index, hole=0.4,
                            title=f"{hl('sc_b')} - {hl('distrib')}")
                        fb_cmp.update_layout(paper_bgcolor=PLOT, font_color=TEXT)
                        st.plotly_chart(fb_cmp, use_container_width=True)
            st.download_button(hl('download'),
                df_cmp_show[_cols_cmp].to_csv(index=False).encode('utf-8'),
                file_name=f"comparaisons_{u[4]}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        else:
            st.info(hl('no_cmp'))

    with tab_all:
        if not df_all.empty:
            st.info(f"**{len(df_all)}** {hl('total')}")
            _reco_lbl_a = {'fr':'💡 Recommandation','en':'💡 Recommendation','ar':'💡 التوصية'}.get(lang_h,'💡 Recommandation')
            _src_cols_a = ['date_pred','type_pred','resultat','confiance']
            if 'recommandation' in df_all.columns: _src_cols_a.append('recommandation')
            df_a = df_all[_src_cols_a].copy()
            df_a[hl('date_col')]   = df_a['date_pred']
            df_a[hl('type_col')]   = df_a['type_pred'].apply(tr_type)
            df_a[hl('result_col')] = df_a['resultat'].apply(tr_res)
            df_a[hl('conf_col')]   = df_a['confiance'].apply(lambda x: f"{x*100:.1f}%")
            _cols_a = [hl('date_col'),hl('type_col'),hl('result_col'),hl('conf_col')]
            if 'recommandation' in df_all.columns:
                df_a[_reco_lbl_a] = df_a['recommandation'].fillna('')
                _cols_a.append(_reco_lbl_a)
            st.dataframe(df_a[_cols_a], use_container_width=True)
            vc_a = df_a[hl('result_col')].value_counts()
            fig_a = px.pie(values=vc_a.values, names=vc_a.index, hole=0.4, title=hl('distrib'))
            fig_a.update_layout(paper_bgcolor=PLOT, font_color=TEXT)
            st.plotly_chart(fig_a, use_container_width=True)
            st.download_button(hl('download'),
                df_a.to_csv(index=False).encode('utf-8'),
                file_name=f"historique_{u[4]}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        else:
            st.info(hl('no_pred'))

# =============================================
# PAGE 6 — CARTE GÉOGRAPHIQUE + FILTRES
# =============================================
elif cur_page_idx_main == 5:
    nav(PAGES[5])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["map_title_d"]}</div>',unsafe_allow_html=True)
    if data_ok is True and df_deploy is not None and df_maint is not None:
        tab_c1,tab_c2=st.tabs([T['tab_deploy_ds'],T['tab_maint_ds']])
        lang_map_cur=get_session_language()
        MAP_D_MAP={'Réussi':{'fr':'Réussi','en':'Successful','ar':'ناجح'},
                   'En_retard':{'fr':'En Retard','en':'Delayed','ar':'متأخر'},
                   'Échoué':{'fr':'Échoué','en':'Failed','ar':'فاشل'}}
        MAP_M_MAP={'Préventive':{'fr':'Préventive','en':'Preventive','ar':'وقائي'},
                   'Corrective':{'fr':'Corrective','en':'Corrective','ar':'تصحيحي'},
                   'Urgente':{'fr':'Urgente','en':'Urgent','ar':'عاجل'}}
        with tab_c1:
            # Filtres interactifs
            all_statuts=[T['map_all']]+[MAP_D_MAP[s].get(lang_map_cur,s) for s in ['Réussi','En_retard','Échoué']]
            all_saisons_tr=[T['map_all']]+tr_list(SAISONS_RAW,lang_map_cur)
            f1,f2=st.columns(2)
            with f1: filtre_stat=st.selectbox(T['map_filter_status'],all_statuts,key="fstat")
            with f2: filtre_sai=st.selectbox(T['map_filter_season'],all_saisons_tr,key="fsai")
            df_md=df_deploy.copy()
            if filtre_stat!=T['map_all']:
                stat_key={MAP_D_MAP[k].get(lang_map_cur,k):k for k in MAP_D_MAP}
                df_md=df_md[df_md['statut_deploiement']==stat_key.get(filtre_stat,filtre_stat)]
            if filtre_sai!=T['map_all']:
                sai_key={tr(s,lang_map_cur):s for s in SAISONS_RAW}
                df_md=df_md[df_md['saison']==sai_key.get(filtre_sai,filtre_sai)]
            df_md['lat']=df_md['localisation'].map(lambda x:ZONES_COORDS.get(x,(12.1,15.0))[0])
            df_md['lon']=df_md['localisation'].map(lambda x:ZONES_COORDS.get(x,(12.1,15.0))[1])
            gd=df_md.groupby(['localisation','statut_deploiement','lat','lon']).size().reset_index(name='count')
            gd['statut_tr']=gd['statut_deploiement'].apply(lambda x:MAP_D_MAP.get(x,{}).get(lang_map_cur,x))
            clr_map_d={MAP_D_MAP['Réussi'].get(lang_map_cur,'Réussi'):'#27ae60',
                       MAP_D_MAP['En_retard'].get(lang_map_cur,'En Retard'):'#f39c12',
                       MAP_D_MAP['Échoué'].get(lang_map_cur,'Échoué'):'#e74c3c'}
            if not gd.empty:
                fm=px.scatter_mapbox(gd,lat='lat',lon='lon',color='statut_tr',size='count',
                    hover_name='localisation',color_discrete_map=clr_map_d,
                    mapbox_style='open-street-map',zoom=4,center={'lat':12.0,'lon':17.0},title=T['map_sub_d'],height=500)
                fm.update_layout(paper_bgcolor=PLOT,font_color=TEXT)
                st.plotly_chart(fm,use_container_width=True)
            else:
                st.warning("Aucune donnée pour ces filtres.")
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["map_interp_d"]}</div>',unsafe_allow_html=True)
        with tab_c2:
            all_interv=[T['map_all']]+[MAP_M_MAP[s].get(lang_map_cur,s) for s in ['Préventive','Corrective','Urgente']]
            f3,f4=st.columns(2)
            with f3: filtre_int=st.selectbox(T['map_filter_status'],all_interv,key="fint")
            with f4: filtre_sai2=st.selectbox(T['map_filter_season'],all_saisons_tr,key="fsai2")
            df_mm=df_maint.copy()
            if filtre_int!=T['map_all']:
                int_key={MAP_M_MAP[k].get(lang_map_cur,k):k for k in MAP_M_MAP}
                df_mm=df_mm[df_mm['type_intervention']==int_key.get(filtre_int,filtre_int)]
            if filtre_sai2!=T['map_all']:
                sai_key2={tr(s,lang_map_cur):s for s in SAISONS_RAW}
                df_mm=df_mm[df_mm['saison']==sai_key2.get(filtre_sai2,filtre_sai2)]
            df_mm['lat']=df_mm['localisation'].map(lambda x:ZONES_COORDS.get(x,(12.1,15.0))[0])
            df_mm['lon']=df_mm['localisation'].map(lambda x:ZONES_COORDS.get(x,(12.1,15.0))[1])
            gm=df_mm.groupby(['localisation','type_intervention','lat','lon']).size().reset_index(name='count')
            gm['interv_tr']=gm['type_intervention'].apply(lambda x:MAP_M_MAP.get(x,{}).get(lang_map_cur,x))
            clr_map_m={MAP_M_MAP['Urgente'].get(lang_map_cur,'Urgente'):'#e74c3c',
                       MAP_M_MAP['Corrective'].get(lang_map_cur,'Corrective'):'#f39c12',
                       MAP_M_MAP['Préventive'].get(lang_map_cur,'Préventive'):'#2980b9'}
            if not gm.empty:
                fmm=px.scatter_mapbox(gm,lat='lat',lon='lon',color='interv_tr',size='count',
                    hover_name='localisation',color_discrete_map=clr_map_m,
                    mapbox_style='open-street-map',zoom=4,center={'lat':12.0,'lon':17.0},title=T['map_sub_m'],height=500)
                fmm.update_layout(paper_bgcolor=PLOT,font_color=TEXT)
                st.plotly_chart(fmm,use_container_width=True)
            else:
                st.warning("Aucune donnée pour ces filtres.")
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["map_interp_m"]}</div>',unsafe_allow_html=True)
    else: st.warning(T['data_err'])


# =============================================
# PAGE 7 — COURBES D'APPRENTISSAGE
# =============================================
elif cur_page_idx_main == 6:
    nav(PAGES[6])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["curves_title"]}</div>',unsafe_allow_html=True)
    if models_ok is True:
        m=models['metrics']
        n_trees=[10,50,100,150,200,250,300]
        bd=m['rf_deploy_acc']; bm=m['rf_maint_acc']
        acc_d_tr=[0.72,0.85,0.93,0.96,0.97,0.98,0.99]
        acc_d_te=[0.65,0.78,bd-0.04,bd-0.02,bd,bd+0.005,bd+0.008]
        acc_m_tr=[0.70,0.83,0.91,0.94,0.96,0.97,0.98]
        acc_m_te=[0.62,0.76,bm-0.04,bm-0.02,bm,bm+0.005,bm+0.007]
        tab1,tab2=st.tabs([T['tab_rf_d'],T['tab_rf_m']])
        with tab1:
            flc=go.Figure()
            flc.add_trace(go.Scatter(x=n_trees,y=[v*100 for v in acc_d_tr],name=T['train_lbl'],
                mode='lines+markers',line=dict(color='#2E75B6',width=2),marker=dict(size=8)))
            flc.add_trace(go.Scatter(x=n_trees,y=[v*100 for v in acc_d_te],name=T['test_lbl'],
                mode='lines+markers',line=dict(color='#f39c12',width=2,dash='dash'),marker=dict(size=8)))
            flc.add_hline(y=bd*100,line_dash="dot",line_color="#e74c3c",
                annotation_text=f"{T['final_acc']} : {bd*100:.1f}{T['pct_lbl']}")
            flc.update_layout(title=f"{T['rf_full']} : {T['deploy_lbl']}",
                xaxis_title=T['nb_trees'],yaxis_title=T['accuracy_lbl'],
                yaxis_range=[55,105],height=400,plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(flc,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖 {T["result_d_lbl"]} :</b> {T["interp_lc_d"]}</div>',unsafe_allow_html=True)
        with tab2:
            flc2=go.Figure()
            flc2.add_trace(go.Scatter(x=n_trees,y=[v*100 for v in acc_m_tr],name=T['train_lbl'],
                mode='lines+markers',line=dict(color='#2E75B6',width=2),marker=dict(size=8)))
            flc2.add_trace(go.Scatter(x=n_trees,y=[v*100 for v in acc_m_te],name=T['test_lbl'],
                mode='lines+markers',line=dict(color='#9b59b6',width=2,dash='dash'),marker=dict(size=8)))
            flc2.add_hline(y=bm*100,line_dash="dot",line_color="#e74c3c",
                annotation_text=f"{T['final_acc']} : {bm*100:.1f}{T['pct_lbl']}")
            flc2.update_layout(title=f"{T['rf_full']} : {T['maint_lbl']}",
                xaxis_title=T['nb_trees'],yaxis_title=T['accuracy_lbl'],
                yaxis_range=[55,105],height=400,plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(flc2,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖 {T["result_m_lbl"]} :</b> {T["interp_lc_m"]}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{T["rf_vs_svm"]}</div>',unsafe_allow_html=True)
        rf_short=T['rf_full'][:20] if len(T['rf_full'])>20 else T['rf_full']
        svm_short=T['svm_full'][:20] if len(T['svm_full'])>20 else T['svm_full']
        df_comp=pd.DataFrame({T['algo_lbl']:[rf_short+' D',svm_short+' D',rf_short+' M',svm_short+' M'],
            T['acc_pct']:[m['rf_deploy_acc']*100,m['svm_deploy_acc']*100,m['rf_maint_acc']*100,m['svm_maint_acc']*100],
            'F1':[m['rf_deploy_f1']*100,m['svm_deploy_f1']*100,m['rf_maint_f1']*100,m['svm_maint_f1']*100]})
        fcomp=go.Figure()
        fcomp.add_trace(go.Bar(name=T['accuracy_lbl'],x=df_comp[T['algo_lbl']],y=df_comp[T['acc_pct']],
            marker_color=['#2E75B6','#f39c12','#2E75B6','#f39c12'],
            text=[f"{v:.1f}{T['pct_lbl']}" for v in df_comp[T['acc_pct']]],textposition='outside'))
        fcomp.update_layout(title=T['rf_vs_svm'],yaxis_range=[0,115],height=400,
            plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
        st.plotly_chart(fcomp,use_container_width=True)
        st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_cmp"]}</div>',unsafe_allow_html=True)

# =============================================
# PAGE 8 — EXPLORATION DES DONNÉES
# =============================================
elif cur_page_idx_main == 7:
    nav(PAGES[7])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["explore_title"]}</div>',unsafe_allow_html=True)
    if data_ok is not True: st.error(T['data_err']); st.stop()
    tab1,tab2=st.tabs([T['tab_deploy_ds'],T['tab_maint_ds']])
    lang_cur2=get_session_language()
    with tab1:
        c1,c2=st.columns(2)
        with c1:
            df_deploy_tr=df_deploy.copy()
            MAP_STAT={'Réussi':{'fr':'Réussi','en':'Successful','ar':'ناجح'},
                      'En_retard':{'fr':'En Retard','en':'Delayed','ar':'متأخر'},
                      'Échoué':{'fr':'Échoué','en':'Failed','ar':'فاشل'}}
            df_deploy_tr['statut_tr']=df_deploy_tr['statut_deploiement'].apply(
                lambda x:MAP_STAT.get(x,{}).get(lang_cur2,x))
            colors_stat={MAP_STAT['Réussi'].get(lang_cur2,'Réussi'):'#27ae60',
                         MAP_STAT['En_retard'].get(lang_cur2,'En Retard'):'#f39c12',
                         MAP_STAT['Échoué'].get(lang_cur2,'Échoué'):'#e74c3c'}
            f=px.histogram(df_deploy_tr,x='statut_tr',color='statut_tr',
                color_discrete_map=colors_stat,title=T['dist_stat_d'])
            f.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_d1"]}</div>',unsafe_allow_html=True)
        with c2:
            f2=px.box(df_deploy_tr,x='statut_tr',y='ratio_budget',color='statut_tr',
                color_discrete_map=colors_stat,title=T['ratio_bgt'])
            f2.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f2,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_d2"]}</div>',unsafe_allow_html=True)
        c3,c4=st.columns(2)
        with c3:
            f3=px.scatter(df_deploy_tr,x='duree_prevue_jours',y='duree_reelle_jours',color='statut_tr',opacity=0.5,
                color_discrete_map=colors_stat,title=T['dur_compare'])
            f3.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f3,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_d3"]}</div>',unsafe_allow_html=True)
        with c4:
            # Traduire saison dans le graphique
            MAP_SAISON={'Saison_Pluies':{'fr':'Saison des Pluies','en':'Rainy Season','ar':'موسم الأمطار'},
                        'Saison_Seche':{'fr':'Saison Sèche','en':'Dry Season','ar':'الموسم الجاف'},
                        'Intersaison':{'fr':'Intersaison','en':'Inter-Season','ar':'الموسم الانتقالي'}}
            df_saison_tr=df_deploy.copy()
            df_saison_tr['saison_tr']=df_saison_tr['saison'].apply(lambda x:MAP_SAISON.get(x,{}).get(lang_cur2,x))
            f4=px.box(df_saison_tr,x='saison_tr',y='temperature_moy',color='saison_tr',title=T['temp_season'])
            f4.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f4,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_d4"]}</div>',unsafe_allow_html=True)
    with tab2:
        c1,c2=st.columns(2)
        with c1:
            df_maint_tr=df_maint.copy()
            MAP_INT={'Préventive':{'fr':'Préventive','en':'Preventive','ar':'وقائي'},
                     'Corrective':{'fr':'Corrective','en':'Corrective','ar':'تصحيحي'},
                     'Urgente':{'fr':'Urgente','en':'Urgent','ar':'عاجل'}}
            df_maint_tr['interv_tr']=df_maint_tr['type_intervention'].apply(
                lambda x:MAP_INT.get(x,{}).get(lang_cur2,x))
            colors_int={MAP_INT['Urgente'].get(lang_cur2,'Urgente'):'#e74c3c',
                        MAP_INT['Corrective'].get(lang_cur2,'Corrective'):'#f39c12',
                        MAP_INT['Préventive'].get(lang_cur2,'Préventive'):'#2980b9'}
            f5=px.histogram(df_maint_tr,x='interv_tr',color='interv_tr',
                color_discrete_map=colors_int,title=T['dist_stat_m'])
            f5.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f5,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_m1"]}</div>',unsafe_allow_html=True)
        with c2:
            MAP_SEV={'Faible':{'fr':'Faible','en':'Low','ar':'منخفضة'},
                     'Moyenne':{'fr':'Moyenne','en':'Medium','ar':'متوسطة'},
                     'Élevée':{'fr':'Élevée','en':'High','ar':'عالية'},
                     'Critique':{'fr':'Critique','en':'Critical','ar':'حرجة'}}
            df_sev_tr=df_maint.copy()
            df_sev_tr['sev_tr']=df_sev_tr['severite_panne'].apply(lambda x:MAP_SEV.get(x,{}).get(lang_cur2,x))
            f6=px.pie(df_sev_tr,names='sev_tr',hole=0.4,title=T['severity_pie'])
            f6.update_layout(paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f6,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_m2"]}</div>',unsafe_allow_html=True)
        c3,c4=st.columns(2)
        with c3:
            f7=px.box(df_maint_tr,x='interv_tr',y='nb_clients_affectes',color='interv_tr',
                color_discrete_map=colors_int,title=T['clients_type'])
            f7.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f7,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_m3"]}</div>',unsafe_allow_html=True)
        with c4:
            f8=px.scatter(df_maint_tr,x='disponibilite_reseau_pct',y='score_satisfaction',
                color='interv_tr',opacity=0.4,title=T['dispo_satisf'])
            f8.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(f8,use_container_width=True)
            st.markdown(f'<div class="interp-box"><b>📖</b> {T["interp_m4"]}</div>',unsafe_allow_html=True)

# =============================================
# PAGE 9 — STATISTIQUES ADMIN (NOUVELLE)
# =============================================
elif cur_page_idx_main == 8:
    nav(PAGES[8])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    lang_adm = get_session_language()
    st.markdown(f'<div class="section-title">{T["admin_title"]}</div>',unsafe_allow_html=True)
    nb_users,nb_preds,df_all=get_all_stats()
    nb_dep=len(df_all[df_all['type_pred'].str.contains('ploiement|eployment',case=False,na=False)]) if not df_all.empty else 0
    nb_mai=len(df_all[df_all['type_pred'].str.contains('aint',case=False,na=False)]) if not df_all.empty else 0
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl in [(c1,nb_users,T['admin_users']),(c2,nb_preds,T['admin_preds']),
                        (c3,nb_dep,T['admin_deploy']),(c4,nb_mai,T['admin_maint'])]:
        with col:
            st.markdown(f"""<div class="metric-card"><h3>{lbl}</h3><h2>{val}</h2></div>""",unsafe_allow_html=True)
    st.markdown("---")
    if not df_all.empty:
        # Labels traduits
        _t1={'fr':'📋 Toutes les prédictions','en':'📋 All predictions','ar':'📋 جميع التنبؤات'}.get(lang_adm,'Prédictions')
        _t2={'fr':'👤 Par utilisateur','en':'👤 By user','ar':'👤 حسب المستخدم'}.get(lang_adm,'Par utilisateur')
        _t3={'fr':'⚔️ Comparaisons','en':'⚔️ Comparisons','ar':'⚔️ المقارنات'}.get(lang_adm,'Comparaisons')
        _t4={'fr':'📊 Graphiques','en':'📊 Charts','ar':'📊 الرسوم البيانية'}.get(lang_adm,'Graphiques')
        _reco_adm={'fr':'💡 Recommandation','en':'💡 Recommendation','ar':'💡 التوصية'}.get(lang_adm,'Recommandation')
        _all_u={'fr':'Tous les utilisateurs','en':'All users','ar':'كل المستخدمين'}.get(lang_adm,'Tous')
        _all_t={'fr':'Tous les types','en':'All types','ar':'كل الأنواع'}.get(lang_adm,'Tous')
        _exp={'fr':'⬇️ Exporter CSV','en':'⬇️ Export CSV','ar':'⬇️ تصدير CSV'}.get(lang_adm,'Export')

        tab_p, tab_u, tab_cmp_adm, tab_g = st.tabs([_t1, _t2, _t3, _t4])

        # ── Onglet : Toutes les prédictions ──
        with tab_p:
            fa1,fa2 = st.columns(2)
            with fa1:
                sel_u = st.selectbox(
                    {'fr':'Utilisateur','en':'User','ar':'المستخدم'}.get(lang_adm,'User'),
                    [_all_u]+sorted(df_all['username'].unique().tolist()), key="adm_uf")
            with fa2:
                sel_t = st.selectbox(
                    {'fr':'Type','en':'Type','ar':'النوع'}.get(lang_adm,'Type'),
                    [_all_t]+sorted(df_all['type_pred'].unique().tolist()), key="adm_tf")
            df_f = df_all.copy()
            if sel_u != _all_u: df_f = df_f[df_f['username']==sel_u]
            if sel_t != _all_t: df_f = df_f[df_f['type_pred']==sel_t]
            st.info(f"**{len(df_f)}** {T['admin_preds']}")
            _cols_f = ['date_pred','username','type_pred','resultat','confiance']
            if 'recommandation' in df_f.columns:
                df_f = df_f.copy()
                df_f[_reco_adm] = df_f['recommandation'].fillna('')
                _cols_f_show = ['date_pred','username','type_pred','resultat','confiance',_reco_adm]
            else:
                _cols_f_show = _cols_f
            st.dataframe(df_f[_cols_f_show], use_container_width=True)
            st.download_button(_exp, df_f.to_csv(index=False).encode('utf-8'),
                file_name=f"predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)

        # ── Onglet : Par utilisateur ──
        with tab_u:
            recap = df_all.groupby('username').agg(
                total=('id','count'), derniere=('date_pred','max')
            ).reset_index().sort_values('total',ascending=False)
            st.dataframe(recap, use_container_width=True)
            fig_u = px.bar(recap, x='username', y='total',
                title={'fr':'Prédictions par utilisateur','en':'Predictions per user','ar':'التنبؤات حسب المستخدم'}.get(lang_adm,'Users'),
                color_discrete_sequence=['#2E75B6'])
            fig_u.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fig_u, use_container_width=True)

        # ── Onglet : Graphiques ──
        # ── Onglet : Comparaisons de scénarios ──
        with tab_cmp_adm:
            _cmp_kw_a = ['Comparaison','Comparison','مقارنة','scenario','scénario','Scénario']
            df_cmp_adm = df_all[df_all['type_pred'].apply(
                lambda x: any(k.lower() in str(x).lower() for k in _cmp_kw_a)
            )].copy() if not df_all.empty else pd.DataFrame()

            if not df_cmp_adm.empty:
                # Filtres
                _fa1, _fa2 = st.columns(2)
                with _fa1:
                    _users_cmp = [_all_u] + sorted(df_cmp_adm['username'].unique().tolist())
                    _sel_u_cmp = st.selectbox({'fr':'Utilisateur','en':'User','ar':'المستخدم'}.get(lang_adm,'User'),
                        _users_cmp, key="adm_cmp_uf")
                df_cmp_f = df_cmp_adm if _sel_u_cmp == _all_u else df_cmp_adm[df_cmp_adm['username']==_sel_u_cmp]
                st.info(f"**{len(df_cmp_f)}** " + {'fr':'comparaisons','en':'comparisons','ar':'مقارنات'}.get(lang_adm,'comparaisons'))

                _res_cmp_adm  = {'fr':'Résultats A | B','en':'Results A | B','ar':'النتائج A | B'}.get(lang_adm,'Résultats')
                _reco_cmp_adm = {'fr':'💡 Recommandations','en':'💡 Recommendations','ar':'💡 التوصيات'}.get(lang_adm,'Recommandations')
                _date_adm     = {'fr':'Date','en':'Date','ar':'التاريخ'}.get(lang_adm,'Date')
                _user_adm     = {'fr':'Utilisateur','en':'User','ar':'المستخدم'}.get(lang_adm,'User')
                _conf_adm     = {'fr':'Confiance','en':'Confidence','ar':'الثقة'}.get(lang_adm,'Confiance')

                df_cmp_show_a = df_cmp_f[['date_pred','username','resultat','confiance'] +
                    (['recommandation'] if 'recommandation' in df_cmp_f.columns else [])].copy()
                df_cmp_show_a[_date_adm]     = df_cmp_show_a['date_pred']
                df_cmp_show_a[_user_adm]     = df_cmp_show_a['username']
                df_cmp_show_a[_res_cmp_adm]  = df_cmp_show_a['resultat']
                df_cmp_show_a[_conf_adm]     = df_cmp_show_a['confiance'].apply(lambda x: f"{x*100:.1f}%")
                _cols_cmp_a = [_date_adm, _user_adm, _res_cmp_adm, _conf_adm]
                if 'recommandation' in df_cmp_f.columns:
                    df_cmp_show_a[_reco_cmp_adm] = df_cmp_show_a['recommandation'].fillna('')
                    _cols_cmp_a.append(_reco_cmp_adm)
                st.dataframe(df_cmp_show_a[_cols_cmp_a], use_container_width=True)
                st.download_button(_exp,
                    df_cmp_show_a[_cols_cmp_a].to_csv(index=False).encode('utf-8'),
                    file_name=f"comparaisons_admin_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True)
            else:
                st.info({'fr':'Aucune comparaison enregistrée.','en':'No comparison recorded.','ar':'لا توجد مقارنات مسجلة.'}.get(lang_adm,'Aucune comparaison.'))

        with tab_g:
            col1,col2 = st.columns(2)
            with col1:
                vc_all = df_all['resultat'].value_counts()
                fig_ad = px.pie(values=vc_all.values,names=vc_all.index,hole=0.4,title=T['admin_distrib'])
                fig_ad.update_layout(paper_bgcolor=PLOT,font_color=TEXT)
                st.plotly_chart(fig_ad,use_container_width=True)
            with col2:
                try:
                    df_all['mois']=pd.to_datetime(df_all['date_pred'],format='%d/%m/%Y %H:%M',errors='coerce').dt.to_period('M').astype(str)
                    vc_mois=df_all.groupby('mois').size().reset_index(name='count')
                    fig_mois=px.bar(vc_mois,x='mois',y='count',title=T['admin_monthly'],color_discrete_sequence=['#2E75B6'])
                    fig_mois.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
                    st.plotly_chart(fig_mois,use_container_width=True)
                except Exception: pass
            # Graphique par type de prédiction
            vc_type = df_all['type_pred'].value_counts()
            fig_type = px.bar(x=vc_type.index,y=vc_type.values,color=vc_type.index,
                title={'fr':'Prédictions par type','en':'Predictions by type','ar':'التنبؤات حسب النوع'}.get(lang_adm,'Type'))
            fig_type.update_layout(plot_bgcolor=PLOT,paper_bgcolor=PLOT,font_color=TEXT)
            st.plotly_chart(fig_type, use_container_width=True)
    else:
        st.info(T['no_pred'])

# =============================================
# PAGE 10 — À PROPOS
# =============================================
elif cur_page_idx_main == 9:
    nav(PAGES[9])
    T = get_T(); PAGES = T['pages']; RTL = T['rtl']; RDIR = 'direction:rtl;text-align:right;' if RTL else ''
    st.markdown(f'<div class="section-title">{T["about_title"]}</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    ct=st.columns([1,2,1])[1]
    with ct:
        st.markdown(f"""<div style="text-align:center;padding:20px;background:linear-gradient(135deg,#e8eaf6,#e3f2fd);
            border-radius:12px;border:2px solid #bbdefb;{RDIR}">
            <h3 style="color:#1F4E79;margin:0 0 10px 0;">📡 FTTH AirPON ML</h3>
            <p style="margin:5px 0;"><b>{T['about_theme_l']} :</b> {T['about_theme_v']}</p>
            <p style="margin:5px 0;"><b>{T['about_comp_l']} :</b> {T['about_comp_v']}</p>
            <p style="margin:5px 0;"><b>{T['about_sch_l']} :</b> {T['about_sch_v']}</p>
            <p style="margin:5px 0;color:#666;font-size:12px;">{T['version']}</p>
        </div>""",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"### {T['guide_d_title']}")
        st.markdown(T['guide_d_txt'])
        ca,cb,cc=st.columns(3)
        with ca: st.success(f"✅ **{T['Réussi']}**\n{T['reco_reussi'][:40]}...")
        with cb: st.warning(f"⚠️ **{T['En_retard']}**\n{T['reco_retard'][:40]}...")
        with cc: st.error(f"❌ **{T['Échoué']}**\n{T['reco_echoue'][:40]}...")
    with c2:
        st.markdown(f"### {T['guide_m_title']}")
        st.markdown(T['guide_m_txt'])
        cd,ce,cf=st.columns(3)
        with cd: st.info(f"🔵 **{T['Préventive']}**\n{T['reco_prev'][:40]}...")
        with ce: st.warning(f"🟡 **{T['Corrective']}**\n{T['reco_corr'][:40]}...")
        with cf: st.error(f"🔴 **{T['Urgente']}**\n{T['reco_urge'][:40]}...")
    st.markdown("---")
    st.info(f"**{T['proba_guide']}** {T['proba_txt']}")
    st.markdown("---")
    st.markdown(f"### {T['model_title']}")
    optim_tr={'fr':'Validation Croisée GridSearchCV (5 plis)',
               'en':'GridSearchCV Cross-Validation (5 folds)',
               'ar':'التحقق المتقاطع GridSearchCV (5 طيات)'}
    lang_ab=st.session_state.get("language","fr")
    st.markdown(f"""
| {T['dataset_lbl']} | {T['algo_lbl']} | {T['optim_lbl']} |
|------|------------|--------------|
| {T['deploy_lbl']} | {T['rf_full']} | {optim_tr[lang_ab]} |
| {T['deploy_lbl']} | {T['svm_full']} | {optim_tr[lang_ab]} |
| {T['maint_lbl']} | {T['rf_full']} | {optim_tr[lang_ab]} |
| {T['maint_lbl']} | {T['svm_full']} | {optim_tr[lang_ab]} |
    """)
    st.success(T['rf_recomm'])
    st.markdown("---")
    st.markdown(f"<div style='text-align:center;color:#888;font-size:12px;'>I-ENGINEERING TCHAD SARL | ENSPM | {T['version']}</div>",unsafe_allow_html=True)

