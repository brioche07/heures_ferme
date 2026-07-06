import streamlit as st
import sqlite3
from datetime import datetime, date

st.set_page_config(page_title="Heures ferme", layout="centered")

st.title("🐄 Suivi heures de travail")

# ---------------- DB ----------------
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

# ---------------- HELPERS ----------------
def format_time(t):
    return t.strftime("%H:%M")

def format_date(d):
    return d.strftime("%d/%m/%Y")

def round_to_30min(dt):
    minutes = dt.minute
    rounded = 30 if minutes > 15 else 0
    return dt.replace(minute=rounded, second=0, microsecond=0)

# ---------------- INPUTS ----------------
st.subheader("➕ Ajouter une session")

date_input = st.date_input("Date", value=date.today())

col1, col2 = st.columns(2)

with col1:
    debut = st.time_input("Début")

with col2:
    fin = st.time_input("Fin")

tache = st.text_input("Tâche (traite, foins, mécanique...)")

# conversion datetime
d1 = datetime.combine(date_input, debut)
d2 = datetime.combine(date_input, fin)

# calcul heures
heures = max(0, (d2 - d1).seconds / 3600)

st.info(f"⏱️ {round(heures, 2)} h")

if st.button("Ajouter"):
    c.execute("""
        INSERT INTO heures (date, debut, fin, heures, tache)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date_input.strftime("%d/%m/%Y"),
        format_time(debut),
        format_time(fin),
        heures,
        tache
    ))
    conn.commit()
    st.success("Ajouté !")

# ---------------- DATA ----------------
st.divider()
st.subheader("📊 Résumé")

c.execute("SELECT date, debut, fin, heures, tache FROM heures ORDER BY id DESC")
rows = c.fetchall()

# total
total = sum(r[3] for r in rows)

# mois / semaine
now = datetime.now()

mois = sum(r[3] for r in rows if now.strftime("%m/%Y") in r[0])
semaine = sum(r[3] for r in rows if now.strftime("%Y") in r[0])  # simple version

# ---------------- STATS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("⏱️ Total", round(total, 2))
col2.metric("📅 Mois", round(mois, 2))
col3.metric("📆 Semaine", round(semaine, 2))

# ---------------- TAUX HORAIRE ----------------
st.subheader("💰 Salaire")

taux = st.number_input("Taux horaire (€)", value=12.0)

st.success(f"💵 Salaire estimé : {round(total * taux, 2)} €")

# ---------------- TABLEAU PROPRE ----------------
st.subheader("📋 Historique")

if rows:
    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aucune donnée")