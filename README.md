# 📡 FTTH_AirPON_ML Système d'Aide à la Décision

> **\Conception et Implémentation d'une Solution Basée sur le Machine Learning pour l'Optimisation du Déploiement et de la Maintenance des Réseaux FTTH AirPON\\**
>
> **\Cas de I-ENGINEERING TCHAD SARL Sous-traitant de Moov Africa Tchad\**

## 🏫 Contexte Académique

|Élément|Détail|
|-|-|
|**École**|École Nationale Supérieure Polytechnique (ENSP) de L'Université de Maroua|
|**Niveau**|Master 2: Ingénieur de Conception / Informatique \& Télécommunications|
|**Spécialité**|Data Science |
|**Entreprise**|I-Engineering Tchad SARL|
|**Activité**|Sous-traitant de Moov Africa Tchad — N'Djamena, Tchad|
|**Année académique**|2025 – 2026|

## 📌 Description du Projet

Cette application est un **système d'aide à la décision** basé sur le Machine Learning, développé pour optimiser les opérations de déploiement et de maintenance des réseaux **FTTH AirPON** (Aerial Passive Optical Network) de **Huawei Technologies**.

Elle permet à I-Engineering Tchad SARL de :

* **Prédire le statut** d'un projet de déploiement FTTH AirPON (Réussi / En retard / Échoué)
* **Recommander le type d'intervention** de maintenance adapté (Préventive / Corrective / Urgente)
* **Visualiser** les données et les performances des modèles via un tableau de bord interactif
* **Comparer des scénarios** de déploiement ou de maintenance
* **Gérer l'historique** des prédictions par utilisateur

## 🚀 Accès à l'Application en Ligne

> ⚡ \*\*Aucune installation requise\*\*  L'application est déployée et accessible directement depuis votre navigateur.

🔗 **URL de l'application :** https://solutionmlftthairpon.streamlit.app/

> 💡 Compatible avec tous les navigateurs modernes (Chrome, Firefox, Edge, Safari).
> Pas besoin d'installer Python ou quoi que ce soit.

## 🌍 Langues Disponibles

L'application est entièrement disponible en **3 langues** :

|Langue|Code|Support RTL|
|-|-|-|
|Français|`fr`|Non|
|English|`en`|Non|
|العربية|`ar`|Oui ✅|

> La langue se sélectionne directement dans la barre latérale de l'application.

## 🖥️ Fonctionnalités — Les 10 Pages

|#|Page|Description|
|-|-|-|
|1|🏠 **Tableau de Bord**|Performances des modèles ML (RF vs SVM), aperçu des datasets|
|2|📦 **Prédiction Déploiement**|Formulaire de prédiction du statut de déploiement + recommandation + rapport HTML|
|3|🔧 **Prédiction Maintenance**|Formulaire de prédiction du type d'intervention + recommandation|
|4|⚔️ **Comparaison Scénarios**|Comparaison côte à côte de deux projets ou incidents|
|5|📊 **Historique**|Historique personnel de toutes les prédictions effectuées|
|6|🗺️ **Carte Géographique**|Visualisation des projets sur carte interactive avec filtres|
|7|📈 **Courbes d'Apprentissage**|Visualisation des performances des modèles ML|
|8|📊 **Exploration des Données**|Statistiques et visualisations des datasets|
|9|📋 **Statistiques Admin**|Tableau de bord administrateur (utilisateurs, prédictions)|
|10|ℹ️ **À Propos**|Guide d'utilisation et informations sur les modèles|

## 🤖 Modèles Machine Learning

### Performances obtenues

|Dataset|Modèle|Accuracy|F1-score|
|-|-|-|-|
|Déploiement (2 000 entrées)|**Random Forest** ⭐|**91,75 %**|**91,71 %**|
|Déploiement (2 000 entrées)|SVM|68,00 %|67,92 %|
|Maintenance (3 000 entrées)|**Random Forest** ⭐|**93,17 %**|**93,18 %**|
|Maintenance (3 000 entrées)|SVM|77,83 %|77,77 %|

> ✅ \*\*Le Random Forest est le modèle retenu\*\* supérieur au SVM de +23,75 pts sur le déploiement et +15,34 pts sur la maintenance.

### Variables cibles

* **Déploiement :** `Réussi` | `En retard` | `Échoué`
* **Maintenance :** `Préventive` | `Corrective` | `Urgente`

### Optimisation

Tous les modèles ont été optimisés par **GridSearchCV** avec une validation croisée à **5 plis**.

## 🔐 Authentification

L'application dispose d'un système d'authentification sécurisé :

* **Inscription** : nom, prénom, email, nom d'utilisateur, mot de passe
* **Connexion** : nom d'utilisateur + mot de passe
* **Sécurité** : mots de passe hashés en **SHA-256**
* **Historique** : chaque utilisateur dispose de son propre historique de prédictions
* **Rôles** : utilisateur standard / administrateur

## 🗂️ Structure des Fichiers du Projet

```
ftth-airpon-ml/
│
├── streamlit\_app.py                          # Application principale
├── translations.py                           # Dictionnaire de traductions FR/EN/AR
├── requirements.txt                          # Dépendances Python
├── users.db                                  # Base de données SQLite (auto-générée)
│
├── dataset\_deploiement\_ftth\_airpon.csv       # Dataset déploiement (2 000 entrées)
├── dataset\_maintenance\_ftth\_airpon.csv       # Dataset maintenance (3 000 entrées)
│
├── best\_rf\_deploiement.pkl                   # Modèle Random Forest — Déploiement
├── best\_svm\_deploiement.pkl                  # Modèle SVM — Déploiement
├── scaler\_deploiement.pkl                    # Normaliseur — Déploiement
├── le\_features\_deploiement.pkl               # Encodeur features — Déploiement
├── le\_target\_deploiement.pkl                 # Encodeur cible — Déploiement
│
├── best\_rf\_maintenance.pkl                   # Modèle Random Forest — Maintenance
├── best\_svm\_maintenance.pkl                  # Modèle SVM — Maintenance
├── scaler\_maintenance.pkl                    # Normaliseur — Maintenance
├── le\_features\_maintenance.pkl               # Encodeur features — Maintenance
├── le\_target\_maintenance.pkl                 # Encodeur cible — Maintenance
│
└── metrics.pkl                               # Métriques de performance des modèles

## 💻 Installation Locale (pour les développeurs)

> ⚠️ Cette section est destinée aux développeurs souhaitant exécuter l'application en local.
> Les utilisateurs finaux peuvent utiliser directement l'application en ligne

### Prérequis

* **Python** 3.9 ou supérieur
* **pip** (gestionnaire de paquets Python)
* **Git** (optionnel, pour cloner le dépôt)

### Étapes d'installation

**1. Cloner le dépôt**

```bash
git clone https://github.com/GERARDMBAIABE/ftth-airpon-ml.git
cd ftth-airpon-ml
```

**2. Créer un environnement virtuel** (recommandé)

```bash
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\\Scripts\\activate
# Sur Linux / macOS :
source venv/bin/activate
```

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**4. Lancer l'application**

```bash
streamlit run streamlit\_app.py
```

**5. Ouvrir dans le navigateur**

L'application s'ouvre automatiquement à l'adresse :

```
http://localhost:8501
```

### Contenu du fichier `requirements.txt`

```
streamlit>=1.35.0
pandas>=2.0.0
scikit-learn==1.6.1
joblib>=1.3.0
plotly>=5.18.0
```

\---

## ☁️ Déploiement en Ligne

L'application est déployée sur **Streamlit Community Cloud** (plateforme gratuite officielle de Streamlit).

### Étapes de déploiement

**1.** Pousser le projet sur **GitHub** 

**2.** Se connecter sur [share.streamlit.io](https://share.streamlit.io) avec un compte GitHub

**3.** Cliquer sur **"New app"** et renseigner :

* Dépôt GitHub : `\GERARDMBAINABE/ftth-airpon-ml`
* Branche : `main`
* Fichier principal : `streamlit\_app.py`

**4.** Cliquer sur **"Deploy"**

> ✅ L'application sera accessible en ligne en quelques minutes via une URL du type :
> `https://\GERARDMBAINABE/ftth-airpon-ml.streamlit.app`

### Notes importantes pour le déploiement

* Le fichier `users.db` est **recréé automatiquement** au démarrage si absent
* Les fichiers `.pkl` (modèles) et `.csv` (données) doivent être inclus dans le dépôt GitHub
* Les fichiers volumineux (> 100 MB) doivent être gérés avec **Git LFS**
* Les fichiers `.pkl` de ce projet sont légers et compatibles avec un dépôt GitHub standard

\---

## 🛠️ Stack Technique

|Technologie|Version|Rôle|
|-|-|-|
|**Python**|3.9+|Langage de programmation principal|
|**Streamlit**|≥ 1.35.0|Interface web — Application multipage|
|**Scikit-learn**|1.6.1|Modèles ML (Random Forest, SVM, GridSearchCV)|
|**Pandas**|≥ 2.0.0|Manipulation et analyse des données|
|**NumPy**|Dernière|Calcul numérique|
|**Plotly**|≥ 5.18.0|Visualisations interactives|
|**Joblib**|≥ 1.3.0|Sauvegarde et chargement des modèles .pkl|
|**SQLite**|Intégré|Base de données utilisateurs et historique|
|**Hashlib**|Intégré|Hashage SHA-256 des mots de passe|

\---

## 📊 Données

Les deux datasets utilisés sont des **données synthétiques** générées avec Python, basées sur les réalités terrain de I-Engineering Tchad SARL :

### Dataset Déploiement

* **2 000 projets** FTTH AirPON simulés
* **Localisations couvertes :** N'Djamena Centre/Sud/Nord, Moundou, Sarh, Abéché, Kélo, Doba, Bongor
* **Variables :** localisation, type de zone, saison, météo, terrain, infrastructure, coûts, équipements, performances réseau, ressources humaines

### Dataset Maintenance

* **3 000 incidents** de maintenance simulés
* **Types d'équipements :** OLT, ONT, Splitter, Câble Fibre Optique, Connecteur, Boîtier Étanche, Antenne AirPON
* **Types de pannes :** Rupture câble, Perte signal, Surtension, Corrosion, Obstruction physique, Défaut connecteur, Panne OLT, Dégradation lente

\---

## 📞 Contact

|Rôle|Nom|Contact
|-|-|-|
|**Auteur**|GERARD MBAINABE|+23566844904/+237659606157|
|**Encadreur académique**|\[Pr.Dr.Ing. Habil Kolyang|
|**Encadreur professionnel**|Massol Harmel Michel|
|**Institution**|Ecole Nationale Supérieure Polytechnique de l'Université de Maroua(ENSPM), Cameroun|
|**Entreprise**|I-Engineering Tchad SARL, N'Djamena, Tchad|

\---

## 📄 Licence

Ce projet est développé dans le cadre d'un mémoire académique de Master 2 à l'Ecole National Supérieure Polytechnique de l'Université de Maroua(ENSPM).
Tous droits réservés a GERARD MBAINABE, et  Engineering Tchad SARL / ENSPM Cameroun qui sont copropriétaire de l'application.

\---

<div align="center">
  <sub>📡 FTTH_AirPON_ML  Version 1.0 | I-Engineering Tchad SARL | ENSPM Cameroun | 2025-2026</sub>
</div>

  
