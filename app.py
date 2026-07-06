import streamlit as st
from datetime import datetime

st.title("🐄 Travail ferme")

# Inputs utilisateur
date = st.date_input("Date")
debut = st.time_input("Heure de début")
fin = st.time_input("Heure de fin")
tache = st.text_input("Tâche")

# Calcul des heures
d1 = datetime.combine(date, debut)
d2 = datetime.combine(date, fin)

if d2 > d1:
    heures = (d2 - d1).seconds / 3600
else:
    heures = 0
    st.warning("Heure de fin doit être après l'heure de début")

# Ajouter les heures
if st.button("Ajouter heures"):
    with open("heures.txt", "a", encoding="utf-8") as f:
        f.write(f"{date};{debut};{fin};{heures};{tache}\n")

# Lire et calculer le total
total = 0
lignes = []

try:
    with open("heures.txt", "r", encoding="utf-8") as f:
        for ligne in f:
            date_, debut_, fin_, heures_, tache_ = ligne.strip().split(";")
            total += float(heures_)
            lignes.append([date_, debut_, fin_, heures_, tache_])
except FileNotFoundError:
    pass

st.subheader(f"⏱️ Heures totales : {round(total, 2)}")

st.dataframe(lignes, use_container_width=True)
