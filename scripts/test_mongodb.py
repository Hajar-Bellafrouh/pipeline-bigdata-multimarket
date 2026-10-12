from pymongo import MongoClient

# 1. Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")

# 2. Accès à la base de données
db = client["multi_market"]

# 3. Accès à la collection
collection = db["commandes"]

# 4. Donnée test
commande_test = {
    "order_id": "CMD001",
    "canal": "web",
    "client_id": "C001",
    "montant_total": 350,
    "statut": "validee"
}

# 5. Insertion dans MongoDB
result = collection.insert_one(commande_test)

print("Commande insérée avec succès, ID :", result.inserted_id)
