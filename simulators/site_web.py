import json
import time
import uuid
import random
from datetime import datetime
import os
from pathlib import Path

# Dossier de sortie
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sources" / "site_web"

os.makedirs(OUTPUT_DIR, exist_ok=True)

produits_catalogue = [
    {"produit_id": "P01", "nom": "Clavier", "prix": 150},
    {"produit_id": "P02", "nom": "Souris", "prix": 80},
    {"produit_id": "P03", "nom": "Écran", "prix": 1200},
    {"produit_id": "P04", "nom": "Casque", "prix": 200}
]

def generer_commande():
    produits = random.sample(produits_catalogue, random.randint(1, 3))
    produits_commande = []
    montant_total = 0

    for p in produits:
        qte = random.randint(1, 3)
        produits_commande.append({
            "produit_id": p["produit_id"],
            "nom": p["nom"],
            "quantite": qte,
            "prix_unitaire": p["prix"]
        })
        montant_total += qte * p["prix"]

    commande = {
        "order_id": str(uuid.uuid4()),
        "canal": "web",
        "date_commande": datetime.now().isoformat(),
        "client_id": f"C{random.randint(100,999)}",
        "produits": produits_commande,
        "montant_total": montant_total,
        "statut": random.choice(["validee", "annulee"]),
        "adresse_livraison": random.choice(
            ["Casablanca", "Rabat", "Tanger", "Marrakech"]
        )
    }

    return commande

while True:
    commande = generer_commande()
    filename = f"commande_{commande['order_id']}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(commande, f, ensure_ascii=False, indent=4)

    print("Commande web générée :", filename)

    time.sleep(random.randint(2, 5))
