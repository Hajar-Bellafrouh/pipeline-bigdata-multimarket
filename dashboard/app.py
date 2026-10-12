# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime
import time

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="MultiMarket Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONNEXION MONGODB ====================
@st.cache_resource
def get_mongo_client():
    """Crée une connexion MongoDB persistante"""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        # Test la connexion
        client.server_info()
        return client
    except Exception as e:
        st.error(f"❌ Impossible de se connecter à MongoDB: {e}")
        st.info("Assurez-vous que MongoDB est en cours d'exécution sur localhost:27017")
        return None

# ==================== CHARGEMENT DES DONNÉES ====================
@st.cache_data(ttl=60)  # Cache pour 60 secondes
def load_data():
    """Charge et transforme les données depuis MongoDB"""
    client = get_mongo_client()
    if client is None:
        return pd.DataFrame()
    
    try:
        db = client["multi_market"]
        collection = db["commandes"]
        
        # Récupère toutes les commandes
        cursor = collection.find({})
        data = list(cursor)
        
        if not data:
            st.warning("Aucune donnée trouvée dans la collection 'commandes'")
            return pd.DataFrame()
        
        # Transforme les données en DataFrame
        records = []
        for doc in data:
            for produit in doc.get('produits', []):
                record = {
                    'order_id': doc.get('order_id'),
                    'client_id': doc.get('client_id'),
                    'produit_id': produit.get('produit_id'),
                    'nom_produit': produit.get('nom'),
                    'quantite': produit.get('quantite', 0),
                    'prix_unitaire': produit.get('prix_unitaire', 0),
                    'canal': doc.get('canal'),
                    'statut': doc.get('statut'),
                    'date_commande': doc.get('date_commande'),
                }
                
                # Ville de livraison (absente pour les commandes en boutique)
                record['ville'] = doc.get('adresse_livraison') or 'Boutique'
                record['adresse'] = doc.get('adresse_livraison') or ''
                
                records.append(record)
        
        df = pd.DataFrame(records)
        
        # Convertit les types
        if not df.empty:
            df['date_commande'] = pd.to_datetime(df['date_commande'], errors='coerce')
            df['total'] = df['quantite'] * df['prix_unitaire']
            df['mois'] = df['date_commande'].dt.strftime('%Y-%m')
            df['annee_mois'] = df['date_commande'].dt.to_period('M')
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.markdown("---")
    
    # Sélecteur de période
    st.subheader("Filtres")
    
    # Bouton de rafraîchissement
    if st.button("🔄 Rafraîchir les données", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.info(f"**Instructions:**\n\n"
            "1. MongoDB doit être en cours d'exécution\n"
            "2. Les données se mettent à jour automatiquement\n"
            "3. Cliquez sur 'Rafraîchir' pour forcer l'actualisation")
    
    # Affiche les stats de connexion
    if get_mongo_client():
        st.success("✅ Connecté à MongoDB")
        db = get_mongo_client()["multi_market"]
        count = db.commandes.count_documents({})
        st.metric("Commandes totales", count)
    
    st.markdown("---")
    st.caption("Dashboard MultiMarket v1.0")

# ==================== TITRE PRINCIPAL ====================
st.title("📊 Dashboard Analytique MultiMarket")
st.markdown("Analyse des commandes multi-canaux en temps réel")
st.markdown("---")

# ==================== CHARGEMENT DES DONNÉES ====================
df = load_data()

if df.empty:
    st.warning("⏳ Chargement des données...")
    time.sleep(2)
    st.rerun()

# ==================== KPI EN HAUT ====================
st.subheader("📈 Indicateurs Clés de Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    ca_total = df['total'].sum() if not df.empty else 0
    st.metric(
        label="Chiffre d'Affaires Total", 
        value=f"{ca_total:,.0f} €",
        delta=f"{len(df):,} transactions"
    )

with col2:
    nb_commandes = df['order_id'].nunique() if not df.empty else 0
    st.metric(
        label="Nombre de Commandes", 
        value=nb_commandes,
        delta=f"{df['client_id'].nunique() if not df.empty else 0} clients"
    )

with col3:
    taux_annulation = (df['statut'] == 'annulee').mean() * 100 if not df.empty else 0
    st.metric(
        label="Taux d'Annulation", 
        value=f"{taux_annulation:.1f}%",
        delta_color="inverse"
    )

with col4:
    panier_moyen = df.groupby('order_id')['total'].sum().mean() if not df.empty else 0
    st.metric(
        label="Panier Moyen", 
        value=f"{panier_moyen:.0f} €",
        delta="par commande"
    )

st.markdown("---")

# ==================== PREMIÈRE LIGNE DE GRAPHIQUES ====================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Chiffre d'Affaires par Mois et Canal")
    
    if not df.empty:
        # Groupement des données
        ca_data = df.groupby(['mois', 'canal'])['total'].sum().reset_index()
        
        fig = px.bar(
            ca_data,
            x='mois',
            y='total',
            color='canal',
            barmode='group',
            labels={'total': 'Chiffre d\'affaires (€)', 'mois': 'Mois', 'canal': 'Canal'},
            color_discrete_map={
                'web': '#1f77b4',
                'mobile': '#ff7f0e',
                'boutique': '#2ca02c'
            }
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible")

with col_right:
    st.subheader("📊 Répartition des Commandes par Canal")
    
    if not df.empty:
        # Données pour le graphique circulaire
        repartition = df.groupby('canal')['order_id'].nunique().reset_index()
        repartition.columns = ['canal', 'nombre_commandes']
        
        fig = px.pie(
            repartition,
            values='nombre_commandes',
            names='canal',
            hole=0.4,
            color='canal',
            color_discrete_map={
                'web': '#1f77b4',
                'mobile': '#ff7f0e',
                'boutique': '#2ca02c'
            }
        )
        
        fig.update_layout(
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible")

# ==================== DEUXIÈME LIGNE DE GRAPHIQUES ====================
st.markdown("---")
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🏆 Top 10 des Produits les Plus Vendus")
    
    if not df.empty:
        # Top 10 produits par quantité
        top_produits = df.groupby(['nom_produit', 'produit_id'])['quantite'].sum().reset_index()
        top_produits = top_produits.sort_values('quantite', ascending=False).head(10)
        
        fig = px.bar(
            top_produits,
            y='nom_produit',
            x='quantite',
            orientation='h',
            color='quantite',
            text='quantite',
            labels={'quantite': 'Quantité vendue', 'nom_produit': 'Produit'},
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible")

with col_right2:
    st.subheader("📉 Taux d'Annulation par Canal")
    
    if not df.empty:
        # Calcul du taux d'annulation
        taux_data = df.groupby('canal').apply(
            lambda x: pd.Series({
                'annulees': (x['statut'] == 'annulee').sum(),
                'totales': len(x),
                'taux': (x['statut'] == 'annulee').mean() * 100
            })
        ).reset_index()
        
        fig = go.Figure()
        
        # Barres pour le taux
        fig.add_trace(go.Bar(
            x=taux_data['canal'],
            y=taux_data['taux'],
            name="Taux d'annulation",
            marker_color=[{'web': '#1f77b4', 'mobile': '#ff7f0e', 'boutique': '#2ca02c'}[c] for c in taux_data['canal']],
            text=taux_data['taux'].round(1).astype(str) + '%',
            textposition='auto'
        ))
        
        fig.update_layout(
            height=500,
            yaxis_title="Taux d'annulation (%)",
            xaxis_title="Canal",
            showlegend=False
        )
        
        # Affiche les nombres exacts
        for i, row in taux_data.iterrows():
            fig.add_annotation(
                x=row['canal'],
                y=row['taux'] + 1,
                text=f"{row['annulees']}/{row['totales']}",
                showarrow=False,
                font=dict(size=10)
            )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible")

# ==================== TROISIÈME LIGNE : CA MOYEN ====================
st.markdown("---")
st.subheader("📈 Chiffre d'Affaires Moyen par Commande et Canal")

if not df.empty:
    # Calcul du CA moyen par commande et par canal
    ca_moyen_data = df.groupby(['canal', 'order_id'])['total'].sum().reset_index()
    ca_moyen = ca_moyen_data.groupby('canal')['total'].mean().reset_index()
    ca_moyen.columns = ['canal', 'ca_moyen']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ca_moyen,
            x='canal',
            y='ca_moyen',
            color='canal',
            text='ca_moyen',
            labels={'ca_moyen': 'CA moyen (€)', 'canal': 'Canal'},
            color_discrete_map={
                'web': '#1f77b4',
                'mobile': '#ff7f0e',
                'boutique': '#2ca02c'
            }
        )
        
        fig.update_layout(
            height=300,
            showlegend=False
        )
        
        fig.update_traces(texttemplate='%{text:.0f} €', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Résumé")
        for _, row in ca_moyen.iterrows():
            st.metric(
                label=f"{row['canal'].title()}",
                value=f"{row['ca_moyen']:.0f} €"
            )
else:
    st.info("Aucune donnée disponible")

# ==================== TABLEAU DES DONNÉES ====================
st.markdown("---")
st.subheader("📋 Aperçu des Données")

if not df.empty:
    with st.expander("Voir les données brutes", expanded=False):
        # Affiche les dernières commandes
        df_display = df.copy()
        df_display['date_commande'] = df_display['date_commande'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Sélection de colonnes
        cols_to_show = ['order_id', 'nom_produit', 'quantite', 'prix_unitaire', 
                       'total', 'canal', 'statut', 'date_commande', 'ville']
        
        st.dataframe(
            df_display[cols_to_show].head(100),
            use_container_width=True,
            height=400
        )
        
        # Téléchargement des données
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données (CSV)",
            data=csv,
            file_name="multimarket_data.csv",
            mime="text/csv"
        )
else:
    st.info("Aucune donnée à afficher")

# ==================== FOOTER ====================
st.markdown("---")
st.caption(
    "Dashboard créé avec Streamlit • Données en direct depuis MongoDB • "
    f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
)