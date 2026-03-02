import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Vendite Online", layout="wide")
st.title("📊 Dashboard - Vendite e Redditività")

# CREAZIONE DATASET

np.random.seed(42)
n = 3000

# Categorie e sotto-categorie
categorie = {
    "Arredamento": ["Sedie", "Tavoli", "Librerie", "Complementi d'arredo"],
    "Forniture per ufficio": ["Raccoglitori", "Carta", "Scaffalature", "Materiale artistico"],
    "Tecnologia": ["Telefoni", "Accessori", "Fotocopiatrici", "Macchine"]
}

# Regioni
regioni = ["Nord-Ovest", "Nord-Est", "Centro", "Sud", "Isole"]

# Province per regione
province = {
    "Nord-Ovest": ["MI", "TO", "GE", "VA"],   # Lombardia, Piemonte, Liguria, Varese
    "Nord-Est": ["VE", "VR", "BO", "TN"],   # Veneto, Veneto, Emilia-Romagna, Trentino
    "Centro": ["RM", "FI", "PG", "LI"],     # Lazio, Toscana, Umbria, Livorno
    "Sud": ["NA", "BA", "PA", "CZ"],        # Campania, Puglia, Sicilia, Calabria
    "Isole": ["CA", "SS", "TP", "AG"]       # Sardegna e Sicilia (provincie)
}

# Generazione casuale delle date
date_ordini = pd.to_datetime(
    np.random.choice(
        pd.date_range("2025-01-01", "2026-03-02"),
        n
    )
)

date_spedizione = date_ordini + pd.to_timedelta(
    np.random.randint(1, 8, n), unit="D"
)

dati = []

for i in range(n):
    categoria = np.random.choice(list(categorie.keys()))
    sotto_categoria = np.random.choice(categorie[categoria])
    regione = np.random.choice(regioni)
    provincia = np.random.choice(province[regione])
    quantita = np.random.randint(1, 10)
    vendite = round(np.random.uniform(20, 1000) * quantita, 2)
    profitto = round(vendite * np.random.uniform(-0.1, 0.3), 2)

    dati.append([
        date_ordini[i],
        date_spedizione[i],
        categoria,
        sotto_categoria,
        vendite,
        profitto,
        regione,
        provincia,
        quantita
    ])

# Creazione del DataFrame con nomi colonne
df_generato = pd.DataFrame(dati, columns=[
    "Data Ordine",
    "Data Spedizione",
    "Categoria",
    "Sotto-Categoria",
    "Vendite",
    "Profitto",
    "Regione",
    "Provincia",
    "Quantità"
])

# Salvataggio del dataset in CSV
df_generato.to_csv("dataset.csv", index=False)

# CARICAMENTO E PULIZIA DATI
df = pd.read_csv("dataset.csv")

# Conversione date
df["Data Ordine"] = pd.to_datetime(df["Data Ordine"], errors="coerce")
df["Data Spedizione"] = pd.to_datetime(df["Data Spedizione"], errors="coerce")

df = df.dropna().drop_duplicates()

# Aggiunta colonne
df["Anno"] = df["Data Ordine"].dt.year
df["Tempo Spedizione (giorni)"] = (df["Data Spedizione"] - df["Data Ordine"]).dt.days

# FILTRI SIDEBAR

st.sidebar.header("Filtri")

year_filter = st.sidebar.multiselect(
    "Anno",
    options=sorted(df["Anno"].unique()),
    default=sorted(df["Anno"].unique())
)

region_filter = st.sidebar.multiselect(
    "Regione",
    options=df["Regione"].unique(),
    default=df["Regione"].unique()
)

category_filter = st.sidebar.multiselect(
    "Categoria",
    options=df["Categoria"].unique(),
    default=df["Categoria"].unique()
)

filtered_df = df[
    (df["Anno"].isin(year_filter)) &
    (df["Regione"].isin(region_filter)) &
    (df["Categoria"].isin(category_filter))
]

# ANALISI - KPI

total_sales = filtered_df["Vendite"].sum()
total_profit = filtered_df["Profitto"].sum()
total_quantity = filtered_df["Quantità"].sum()
avg_shipping = filtered_df["Tempo Spedizione (giorni)"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Totale Vendite (€)", f"{total_sales:,.0f}".replace(",", "."))
col2.metric("Totale Profitto (€)", f"{total_profit:,.0f}".replace(",", "."))
col3.metric("Quantità Venduta", f"{total_quantity:,.0f}".replace(",", "."))
col4.metric("Giorni Medi Spedizione", f"{avg_shipping:,.2f}".replace(".", ","))

st.markdown("---")

# ANALISI VENDITE PER ANNO

sales_year = (
    filtered_df.groupby("Anno")[["Vendite", "Profitto"]]
    .sum()
    .reset_index()
)

fig1 = px.line(
    sales_year,
    x="Anno",
    y=["Vendite", "Profitto"],
    markers=True,
    title="Vendite e Profitti per Anno"
)

st.plotly_chart(fig1, use_container_width=True)


#TOP 5 SOTTOCATEGORIE

top5 = (
    filtered_df.groupby("Sotto-Categoria")["Vendite"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

fig2 = px.bar(
    top5,
    x="Sotto-Categoria",
    y="Vendite",
    title="Top 5 Sottocategorie per Vendite",
    color="Vendite"
)

st.plotly_chart(fig2, use_container_width=True)


#VENDITE PER PROVINCIA

sales_provincia = (
    filtered_df.groupby("Provincia")["Vendite"]
    .sum()
    .reset_index()
)

fig3 = px.bar(
    sales_provincia,
    x="Provincia",
    y="Vendite",
    title="Vendite per Provincia",
    color="Vendite"
)

st.plotly_chart(fig3, use_container_width=True)