import streamlit as st
import joblib
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Système intelligent de détection automatique des cyberattaques",
    page_icon="🚨",
    layout="wide"
)

# =========================
# Son d'alerte
# =========================
def jouer_son_alerte(index):
    components.html(f"""
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg?attaque={index}" type="audio/ogg">
        </audio>
    """, height=0)

# =========================
# Chargement modèle + données
# =========================
@st.cache_resource
def charger_modele():
    return joblib.load("models/random_forest_model.pkl")

@st.cache_data
def charger_donnees():
    X_test = joblib.load("dataset/X_test.pkl")
    y_test = joblib.load("dataset/y_test_binary.pkl")
    return X_test, y_test

modele = charger_modele()
X_test, y_test = charger_donnees()
seuil = 0.10

# =========================
# Session state
# =========================
if "page" not in st.session_state:
    st.session_state["page"] = "Tableau de bord"

if "derniere_alerte" not in st.session_state:
    st.session_state["derniere_alerte"] = None

if "historique_alertes" not in st.session_state:
    st.session_state["historique_alertes"] = []

if "monitoring" not in st.session_state:
    st.session_state["monitoring"] = False

if "index_actuel" not in st.session_state:
    st.session_state["index_actuel"] = 0

if "normal_count" not in st.session_state:
    st.session_state["normal_count"] = 0

# =========================
# Sidebar
# =========================
st.sidebar.title("Navigation")

if st.sidebar.button("🏠 Tableau de bord"):
    st.session_state["page"] = "Tableau de bord"

if st.sidebar.button("🛡️ Surveillance"):
    st.session_state["page"] = "Surveillance"

if st.sidebar.button("🚨 Détails de l'alerte"):
    st.session_state["page"] = "Détails"

if st.sidebar.button("📜 Historique des alertes"):
    st.session_state["page"] = "Historique"

if st.sidebar.button("ℹ️ À propos"):
    st.session_state["page"] = "À propos"

page = st.session_state["page"]

# =========================
# PAGE 1 : TABLEAU DE BORD
# =========================
if page == "Tableau de bord":
    st.title("Système intelligent de détection automatique des cyberattaques")
    st.caption("Surveillance du trafic réseau et génération automatique d’alertes")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("État du système", "Actif")
    col2.metric("Modèle utilisé", "Random Forest")
    col3.metric("Seuil de détection", f"{seuil:.2f}")
    col4.metric("Nombre d’alertes", len(st.session_state["historique_alertes"]))

    st.markdown("---")

    gauche, droite = st.columns([2, 1])

    with gauche:
        st.subheader("Présentation du système")
        st.write("""
Cette application permet de détecter automatiquement les cyberattaques à l’aide d’un modèle de machine learning.
Le système analyse les enregistrements réseau, estime la probabilité d’une attaque, puis génère une alerte visuelle et sonore lorsque le comportement détecté est suspect.
        """)

    with droite:
        st.subheader("État actuel")
        if st.session_state["derniere_alerte"] is None:
            st.success("Aucune menace détectée pour le moment.")
        else:
            if st.session_state["derniere_alerte"]["classe_predite"] == "Attaque":
                st.error("Alerte active : menace détectée")
            else:
                st.success("Dernier trafic analysé : normal")

    st.markdown("---")
    st.subheader("Dernière activité")

    if st.session_state["derniere_alerte"] is not None:
        alerte = st.session_state["derniere_alerte"]
        st.write(f"**Heure :** {alerte['heure']}")
        st.write(f"**Index analysé :** {alerte['index']}")
        st.write(f"**Résultat prédit :** {alerte['classe_predite']}")
        st.write(f"**Probabilité d’attaque :** {alerte['probabilite']:.4f}")
        st.write(f"**Niveau de risque :** {alerte['niveau_risque']}")

        if alerte["classe_predite"] == "Attaque":
            if st.button("Voir les détails de la dernière alerte"):
                st.session_state["page"] = "Détails"
                st.rerun()
    else:
        st.info("Aucune analyse n’a encore été lancée.")
        # =========================
    # Affichage des images
    # =========================
    st.subheader("Résultats des évaluations du modèle")

    # Affichage des images des résultats
    st.image("graphs/evaluation_metrics.png", caption="Evaluation Metrics")
    st.image("graphs/confusion_matrix.png", caption="Confusion Matrix")
    st.image("graphs/roc_curve.png", caption="ROC Curve")
    st.image("graphs/feature_importance.png", caption="Feature Importance")

    st.markdown("---")
    st.subheader("Dernière activité")
    if st.session_state["derniere_alerte"] is not None:
        alerte = st.session_state["derniere_alerte"]
        st.write(f"Heure : {alerte['heure']}")
        st.write(f"Index analysé : {alerte['index']}")
        st.write(f"Résultat prédit : {alerte['classe_predite']}")
        st.write(f"Probabilité d’attaque : {alerte['probabilite']:.4f}")
        st.write(f"Niveau de risque : {alerte['niveau_risque']}")

        if alerte["classe_predite"] == "Attaque":
            if st.button("Voir les détails de la dernière alerte"):
                st.session_state["page"] = "Détails"
                st.rerun()
    else:
        st.info("Aucune analyse n’a encore été lancée.")

# =========================
# PAGE 2 : SURVEILLANCE REAL-TIME
# =========================
elif page == "Surveillance":
    st.title("Surveillance automatique en temps réel")
    st.write("Le système analyse automatiquement les enregistrements du jeu de test, un par un.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Index actuel", st.session_state["index_actuel"])
    col2.metric("Alertes détectées", len(st.session_state["historique_alertes"]))
    col3.metric("Trafic normal", st.session_state["normal_count"])
    

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("▶️ Démarrer la surveillance"):
            st.session_state["monitoring"] = True

    with c2:
        if st.button("⏸️ Arrêter"):
            st.session_state["monitoring"] = False

    with c3:
        if st.button("🔄 Réinitialiser"):
            st.session_state["monitoring"] = False
            st.session_state["index_actuel"] = 0
            st.session_state["derniere_alerte"] = None
            st.session_state["historique_alertes"] = []
            st.session_state["normal_count"] = 0
            st.rerun()

    st.markdown("---")

    if st.session_state["monitoring"]:
        st.success("🟢 Surveillance active...")

        if st.session_state["index_actuel"] < len(X_test):
            index_record = st.session_state["index_actuel"]
            record = X_test.iloc[[index_record]]

            probabilite = modele.predict_proba(record)[0][1]
            prediction = 1 if probabilite >= seuil else 0
            classe_reelle = int(y_test[index_record])

            classe_predite = "Attaque" if prediction == 1 else "Normal"
            classe_reelle_label = "Attaque" if classe_reelle == 1 else "Normal"
            heure_detection = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if probabilite >= 0.80:
                niveau_risque = "Élevé 🔴"
                recommandation = "Bloquer immédiatement la source suspecte et examiner les journaux système."
            elif probabilite >= 0.50:
                niveau_risque = "Moyen 🟠"
                recommandation = "Surveiller le trafic et vérifier la source de l’activité."
            else:
                niveau_risque = "Faible 🟢"
                recommandation = "Effectuer une vérification simple et continuer la surveillance."

            st.session_state["derniere_alerte"] = {
                "heure": heure_detection,
                "index": int(index_record),
                "probabilite": float(probabilite),
                "prediction": int(prediction),
                "classe_predite": classe_predite,
                "classe_reelle": classe_reelle_label,
                "seuil": seuil,
                "niveau_risque": niveau_risque,
                "recommandation": recommandation
            }

            st.subheader("Résultat de l’analyse")

            r1, r2, r3, r4 = st.columns(4)
            r1.info(f"Index : {index_record}")
            r2.info(f"Probabilité : {probabilite:.4f}")
            r3.info(f"Résultat : {classe_predite}")
            r4.info(f"Risque : {niveau_risque}")

            if prediction == 1:
                jouer_son_alerte(index_record)
                st.toast("🚨 Alerte automatique : attaque détectée", icon="🚨")
                st.error("🚨 Une activité suspecte a été détectée automatiquement.")
                st.warning(f"🧠 Recommandation : {recommandation}")

                st.session_state["historique_alertes"].append({
                    "Heure": heure_detection,
                    "Index": int(index_record),
                    "Probabilité": round(probabilite, 4),
                    "Classe prédite": classe_predite,
                    "Classe réelle": classe_reelle_label,
                    "Niveau de risque": niveau_risque,
                    "Recommandation": recommandation
                })

                if st.button("Voir les détails de l’alerte"):
                    st.session_state["page"] = "Détails"
                    st.rerun()
            else:
                st.session_state["normal_count"] += 1
                st.success("✅ Trafic normal détecté.")

            st.markdown("---")
            st.subheader("Aperçu des caractéristiques analysées")
            st.dataframe(record)

            st.session_state["index_actuel"] += 1
            time.sleep(2)
            st.rerun()

        else:
            st.session_state["monitoring"] = False
            st.warning("Fin de la surveillance : tous les enregistrements ont été analysés.")
    else:
        st.info("Cliquez sur « Démarrer la surveillance » pour lancer l’analyse automatique.")

    st.markdown("---")
    st.subheader("📊 Statistiques de surveillance")

    total_alertes = len(st.session_state["historique_alertes"])
    total_normal = st.session_state["normal_count"]

    if total_alertes == 0 and total_normal == 0:
        st.info("Aucune donnée analysée pour afficher le graphique.")
    else:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(["Attaques", "Normal"], [total_alertes, total_normal])
        ax.set_title("Attaques détectées vs trafic normal")
        ax.set_ylabel("Nombre")
        st.pyplot(fig)

# =========================
# PAGE 3 : DETAILS
# =========================
elif page == "Détails":
    st.title("Détails de l’alerte")

    if st.session_state["derniere_alerte"] is None:
        st.info("Aucune alerte disponible. Veuillez lancer une analyse d’abord.")
    else:
        alerte = st.session_state["derniere_alerte"]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Heure de détection :** {alerte['heure']}")
            st.write(f"**Index analysé :** {alerte['index']}")
            st.write(f"**Résultat prédit :** {alerte['classe_predite']}")

        with col2:
            st.write(f"**Probabilité d’attaque :** {alerte['probabilite']:.4f}")
            st.write(f"**Classe réelle :** {alerte['classe_reelle']}")
            st.write(f"**Seuil de détection :** {alerte['seuil']:.2f}")

        st.markdown("---")
        st.subheader("Niveau de risque")

        if alerte["classe_predite"] == "Attaque":
            if alerte["probabilite"] >= 0.80:
                st.error("Niveau de risque : Élevé")
            elif alerte["probabilite"] >= 0.50:
                st.warning("Niveau de risque : Moyen")
            else:
                st.info("Niveau de risque : Faible")
        else:
            st.success("Niveau de risque : Aucun")

        st.markdown("---")
        st.subheader("Recommandations")

        if alerte["classe_predite"] == "Attaque":
            st.warning(alerte["recommandation"])
        else:
            st.success("Aucune action immédiate n’est nécessaire.")

        st.markdown("---")
        st.subheader("Données de l’enregistrement analysé")
        record = X_test.iloc[[alerte["index"]]]
        st.dataframe(record.T)

# =========================
# PAGE 4 : HISTORIQUE
# =========================
elif page == "Historique":
    st.title("Historique des alertes")

    if len(st.session_state["historique_alertes"]) == 0:
        st.info("Aucune alerte enregistrée pour le moment.")
    else:
        historique_df = pd.DataFrame(st.session_state["historique_alertes"])
        st.dataframe(historique_df, use_container_width=True)

        st.download_button(
            label="📥 Télécharger l’historique en CSV",
            data=historique_df.to_csv(index=False).encode("utf-8"),
            file_name="historique_alertes.csv",
            mime="text/csv"
        )

        if st.button("🗑️ Effacer l’historique"):
            st.session_state["historique_alertes"] = []
            st.rerun()

# =========================
# PAGE 5 : A PROPOS
# =========================
elif page == "À propos":
    st.title("À propos du projet")
    st.write("""
Cette application représente une démonstration d’un système intelligent de détection automatique des cyberattaques.

### Fonctionnalités principales :
- surveillance automatique en temps réel des enregistrements réseau ;
- prédiction automatique par modèle de machine learning ;
- génération d’une alerte visuelle et sonore ;
- classification du niveau de risque ;
- recommandations intelligentes ;
- affichage détaillé de la menace détectée ;
- sauvegarde et exportation de l’historique des alertes en CSV.

### Modèle utilisé :
Random Forest Classifier
    """)
