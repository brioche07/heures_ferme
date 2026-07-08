import streamlit as st
from supabase import create_client
from datetime import datetime, date, time, timedelta
import pandas as pd


# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="Heures ferme",
    page_icon="🐄",
    layout="centered"
)


# ---------------- SUPABASE ----------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# ---------------- FONCTIONS ----------------

def heure_format(h):
    return h.strftime("%H:%M")


def calcul_heures(debut, fin):
    d1 = datetime.combine(date.today(), debut)
    d2 = datetime.combine(date.today(), fin)

    if d2 <= d1:
        return 0

    return round((d2 - d1).seconds / 3600, 2)



# ---------------- AUTO MATIN SOIR ----------------

maintenant = datetime.now()

heure_actuelle = maintenant.hour

date_defaut = date.today()

debut_defaut = time(7, 0)
fin_defaut = time(9, 0)
tache_defaut = "matin"


if heure_actuelle >= 17:
    debut_defaut = time(17, 0)
    fin_defaut = time(19, 0)
    tache_defaut = "soir"


# ---------------- TITRE ----------------

st.title("Mes heures")


# ---------------- AJOUT ----------------

date_travail = st.date_input(
    "Date",
    value=date_defaut
)


col1, col2 = st.columns(2)

with col1:
    debut = st.time_input(
        "Début",
        value=debut_defaut
    )

with col2:
    fin = st.time_input(
        "Fin",
        value=fin_defaut
    )


tache = st.text_input(
    "Tâche",
    value=tache_defaut
)


heures = calcul_heures(debut, fin)


st.info(
    f"⏱️ Durée : {heures} heures"
)



if st.button("Ajouter"):

    supabase.table("heures").insert(
        {
            "date": date_travail.strftime("%Y-%m-%d"),
            "debut": heure_format(debut),
            "fin": heure_format(fin),
            "heures": heures,
            "tache": tache
        }
    ).execute()


    st.success("Heures ajoutées !")

    st.rerun()



# ---------------- RECUPERATION DONNEES ----------------

resultat = (
    supabase
    .table("heures")
    .select("*")
    .order("id", desc=True)
    .execute()
)


donnees = resultat.data



# ---------------- STATISTIQUES ----------------

st.divider()

st.subheader("📊 Résumé")


if donnees:

    df = pd.DataFrame(donnees)


    df["date"] = pd.to_datetime(df["date"])


    total = df["heures"].sum()


    aujourd_hui = datetime.now()


    debut_semaine = aujourd_hui - timedelta(
        days=aujourd_hui.weekday()
    )


    heures_semaine = df[
        df["date"] >= debut_semaine
    ]["heures"].sum()


    heures_mois = df[
        (df["date"].dt.month == aujourd_hui.month)
        &
        (df["date"].dt.year == aujourd_hui.year)
    ]["heures"].sum()



    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total",
        f"{total:.2f} h"
    )

    c2.metric(
        "Cette semaine",
        f"{heures_semaine:.2f} h"
    )

    c3.metric(
        "Ce mois",
        f"{heures_mois:.2f} h"
    )


    # ---------------- SALAIRE ----------------

    st.subheader("💰 Salaire")


    taux = 9.5


    st.success(
        f"Salaire estimé : {total*taux:.2f} €"
    )



    # ---------------- TABLEAU ----------------


    st.subheader("📋 Historique")


    affichage = df.copy()


    affichage["date"] = affichage["date"].dt.strftime(
        "%d/%m/%Y"
    )


    affichage = affichage[
        [
            "date",
            "debut",
            "fin",
            "heures",
            "tache"
        ]
    ]


    affichage.columns = [
        "Date",
        "Début",
        "Fin",
        "Heures",
        "Tâche"
    ]


    st.dataframe(
        affichage,
        hide_index=True,
        use_container_width=True
    )


else:

    st.info(
        "Aucune heure enregistrée"
    )
