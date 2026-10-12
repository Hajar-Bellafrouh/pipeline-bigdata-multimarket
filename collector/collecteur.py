import os
import json
import time
import shutil
from pathlib import Path
from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["multi_market"]
collection = db["commandes"]

# Dossiers (chemins relatifs à la racine du projet, indépendants du dossier d'exécution)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCE_DIRS = [
    DATA_DIR / "sources" / "site_web",
    DATA_DIR / "sources" / "application_mobile",
    DATA_DIR / "sources" / "boutique_physique",
]
ARCHIVE_DIR = DATA_DIR / "archive"

for d in SOURCE_DIRS:
    os.makedirs(d, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def traiter_fichier_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insertion dans MongoDB
        collection.insert_one(data)
        print("Inséré dans MongoDB :", os.path.basename(filepath))

        # Déplacement vers archive
        shutil.move(filepath, os.path.join(ARCHIVE_DIR, os.path.basename(filepath)))
        print("Archivé :", os.path.basename(filepath))

    except Exception as e:
        print("Erreur avec le fichier", filepath, ":", e)

# Boucle principale
while True:
    for source_dir in SOURCE_DIRS:
        for filename in os.listdir(source_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(source_dir, filename)
                traiter_fichier_json(filepath)

    time.sleep(5)  # pause de 5 secondes
