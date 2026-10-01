"""
Script de diagnostic — FTTH AirPON ML
Lance ce script depuis le dossier projet pour identifier les fichiers manquants.
Usage : python diagnostic.py
"""
import os, sys

print("=" * 60)
print("  DIAGNOSTIC FTTH AirPON ML — Vérification des fichiers")
print("=" * 60)

# Dossier courant
cwd = os.getcwd()
print(f"\n📁 Dossier courant : {cwd}")
print(f"📁 Contenu :")
for item in sorted(os.listdir(cwd)):
    print(f"   {'📁' if os.path.isdir(item) else '📄'} {item}")

# Fichiers attendus
MODELES = [
    'best_rf_deploiement.pkl',
    'best_svm_deploiement.pkl',
    'scaler_deploiement.pkl',
    'le_target_deploiement.pkl',
    'le_features_deploiement.pkl',
    'best_rf_maintenance.pkl',
    'best_svm_maintenance.pkl',
    'scaler_maintenance.pkl',
    'le_target_maintenance.pkl',
    'le_features_maintenance.pkl',
    'metrics.pkl',
]
DONNEES = [
    'dataset_deploiement_ftth_airpon.csv',
    'dataset_maintenance_ftth_airpon.csv',
]
AUTRES = [
    'translations.py',
    'requirements.txt',
]

def chercher(filename, dossier):
    """Cherche récursivement un fichier."""
    for root, dirs, files in os.walk(dossier):
        if filename in files:
            return os.path.join(root, filename)
    return None

print("\n" + "=" * 60)
print("  MODÈLES (.pkl)")
print("=" * 60)
manquants_m = []
for f in MODELES:
    chemin = chercher(f, cwd)
    if chemin:
        print(f"  ✅ {f}")
        print(f"     → {chemin}")
    else:
        print(f"  ❌ MANQUANT : {f}")
        manquants_m.append(f)

print("\n" + "=" * 60)
print("  DONNÉES (.csv)")
print("=" * 60)
manquants_d = []
for f in DONNEES:
    chemin = chercher(f, cwd)
    if chemin:
        print(f"  ✅ {f}")
        print(f"     → {chemin}")
    else:
        print(f"  ❌ MANQUANT : {f}")
        manquants_d.append(f)

print("\n" + "=" * 60)
print("  AUTRES FICHIERS")
print("=" * 60)
for f in AUTRES:
    chemin = chercher(f, cwd)
    if chemin:
        print(f"  ✅ {f} → {chemin}")
    else:
        print(f"  ❌ MANQUANT : {f}")

print("\n" + "=" * 60)
print("  RÉSUMÉ")
print("=" * 60)
total_manquants = len(manquants_m) + len(manquants_d)
if total_manquants == 0:
    print("  ✅ Tous les fichiers sont présents !")
    print("  ✅ Lance l'app avec : streamlit run app\\streamlit_app.py")
else:
    print(f"  ❌ {total_manquants} fichier(s) manquant(s) !")
    print("\n  SOLUTION :")
    print("  Place les fichiers manquants dans la bonne structure :")
    print("""
  Solution_ML_FTTH_AirPON\\
  ├── app\\
  │   └── streamlit_app.py
  ├── models\\
  │   ├── deploiement\\
  │   │   ├── best_rf_deploiement.pkl
  │   │   ├── best_svm_deploiement.pkl
  │   │   ├── scaler_deploiement.pkl
  │   │   ├── le_target_deploiement.pkl
  │   │   └── le_features_deploiement.pkl
  │   ├── maintenance\\
  │   │   ├── best_rf_maintenance.pkl
  │   │   ├── best_svm_maintenance.pkl
  │   │   ├── scaler_maintenance.pkl
  │   │   ├── le_target_maintenance.pkl
  │   │   └── le_features_maintenance.pkl
  │   └── metrics.pkl
  ├── data\\
  │   ├── deploiement\\
  │   │   └── dataset_deploiement_ftth_airpon.csv
  │   └── maintenance\\
  │       └── dataset_maintenance_ftth_airpon.csv
  ├── translations.py
  └── requirements.txt
  """)

print("=" * 60)
input("\nAppuie sur Entrée pour fermer...")
