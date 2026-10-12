# Projet BI NoSQL – MultiMarket

Chaîne Big Data de commandes multi-canaux (web, mobile, boutique) : simulateurs → collecteur → MongoDB → dashboard Streamlit / Power BI.

## Architecture

```
simulateurs (3 canaux)  ──JSON──▶  data/sources/<canal>/
                                        │
                              collector/collecteur.py
                                        │ insert              ┌▶ dashboard/app.py (Streamlit)
                                        ▼                     │
                       MongoDB  multi_market.commandes  ──────┴▶ powerbi/projet_BI_NoSQL.pbix
                                        │
                                  data/archive/  (JSON traités)
```

## Structure

```
projet_BI/
├── simulators/        # site_web.py, application_mobile.py, boutique_physique.py
├── collector/         # collecteur.py (JSON → MongoDB, puis archivage)
├── dashboard/         # app.py (Streamlit)
├── scripts/           # test_mongodb.py (test de connexion/insertion)
├── data/
│   ├── sources/       # dossiers de dépôt des simulateurs (un par canal)
│   └── archive/       # commandes déjà collectées (échantillon)
├── powerbi/           # projet_BI_NoSQL.pbix
├── requirements.txt
└── README.md
```

## Prérequis

- Python 3.9+
- MongoDB en cours d'exécution sur `localhost:27017`

```bash
pip install -r requirements.txt
```

## Lancement

Depuis la racine du projet, dans des terminaux séparés (les chemins sont indépendants du dossier courant) :

```bash
python simulators/site_web.py
python simulators/application_mobile.py
python simulators/boutique_physique.py
python collector/collecteur.py
streamlit run dashboard/app.py
```

Test de MongoDB : `python scripts/test_mongodb.py`

## Format d'une commande

`order_id`, `canal` (`web` / `mobile` / `boutique`), `date_commande`, `client_id`, `produits[]` (`produit_id`, `nom`, `quantite`, `prix_unitaire`), `montant_total`, `statut` (`validee` / `annulee`), `adresse_livraison` (absent pour la boutique).

##  Auteurs

- **Bellafrouh Hajar**
- **Foudal Ihsane**
- **Gourri Hiba**

Filière IID2