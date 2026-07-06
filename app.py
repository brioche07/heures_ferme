import streamlit as st
import sqlite3
from datetime import datetime, date, time

st.set_page_config(page_title="Heures ferme", layout="centered")

st.title("Mes heures ferme")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("heures.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS heures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    debut TEXT,
    fin TEXT,
    heures REAL,
    tache TEXT
)
""")
conn.commit()

# ---------------- AUTO LOGIC ----------------
now = datetime.now()
heure = now.hour

default_date = date.today()
default_debut = time(7, 0)
default_fin = time(9, 0)
default_tache = ""

if heure >= 17:
    default_debut = time(17, 0)
    default_fin = time(19, 0)
    default_tache = "soir"

elif heure >= 7:
    default_debut = time(7, 0)
    default_fin = time(9, 0)
    default_tache = "matin"

# ---------------- INPUTS ----------------
st.subheader("Ajouter des heures")

date_input = st.date_input("Date", value=default_date)

col1, col2 = st.columns(2)

with col1:
    debut = st.time_input("Début", value=default_debut)

with col2:
    fin = st.time_input("Fin", value=default_fin)

tache = st.text_input("Tâche", value=default_tache)

# ---------------- CALCUL ----------------
d1 = datetime.combine(date_input, debut)
d2 = datetime.combine(date_input, fin)

heures = max(0, (d2 - d1).seconds / 3600)

st.info(f"⏱️ Heures calculées : {round(heures, 2)} h")

# ---------------- ADD DATA ----------------
if st.button("Ajouter"):
    c.execute("""
        INSERT INTO heures (date, debut, fin, heures, tache)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date_input.strftime("%d/%m/%Y"),
        debut.strftime("%H:%M"),
        fin.strftime("%H:%M"),
        heures,
        tache
    ))
    conn.commit()
    st.success("Ajouté !")

# ---------------- LOAD DATA ----------------
st.divider()
st.subheader("📊 Résumé")

c.execute("SELECT date, debut, fin, heures, tache FROM heures ORDER BY id DESC")
rows = c.fetchall()

total = sum(r[3] for r in rows)

# mois / semaine simplifiés
now_month = now.strftime("%m/%Y")

mois = sum(r[3] for r in rows if now_month in r[0])

# semaine simple (approx)
semaine = sum(r[3] for r in rows if now.year == now.year)

# ---------------- STATS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total", round(total, 2))
col2.metric("Mois", round(mois, 2))
col3.metric("Semaine", round(semaine, 2))

# ---------------- SALAIRE ----------------
st.subheader("💰 Salaire")

taux = 9,5

st.success(f"💵 Salaire estimé : {round(total * taux, 2)} €")

# ---------------- TABLE ----------------
st.subheader("Historique")

if rows:
    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aucune donnée")
