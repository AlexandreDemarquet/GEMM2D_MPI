import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 Benchmark de GEMM Distribué")
st.markdown("""
Ce tableau de bord montre les performances des différents algorithmes de multiplication de matrices distribuée en MPI :
- **p2p**
- **bcast**
- **p2p-i-la** (avec lookahead)

Les résultats sont issus du fichier `bench.csv` généré par le script shell.
""")


l_results = ["./results/results_bin_tree256.csv", "./results/results_crossbar.csv", "./results/results_ring_256.csv","results_de_test.csv", "test_config.csv"]


selected_results = st.selectbox("Choisir les resultats", l_results)

# Chargement des données
@st.cache_data
def load_data(nom_csv):
    df = pd.read_csv(nom_csv)
    df["P"] = df["p"] * df["q"]
    return df

df = load_data(selected_results)

# Filtrage interactif
col1, col2 = st.columns(2)
with col1:
    selected_algos = st.multiselect("Choisir les algorithmes", df["algo"].unique(), default=df["algo"].unique())
with col2:
    b_values = sorted(df["b"].unique())
    selected_b = st.selectbox("Taille de bloc (b)", b_values)

filtered = df[(df["algo"].isin(selected_algos)) & (df["b"] == selected_b)]

# Sélection unique
choix = st.selectbox(
    "Choisissez une forme de grille :",
    ("Aucun filtre", "Carrée (p == q)", "Plus de lignes (p > q)", "Plus de colonnes (p < q)")
)

# Appliquer le filtre selon le choix
if choix == "Carrée (p == q)":
    filtered = df[df["p"] == df["q"]]
elif choix == "Plus de lignes (p > q)":
    filtered = df[df["p"] > df["q"]]
elif choix == "Plus de colonnes (p < q)":
    filtered = df[df["p"] < df["q"]]
else:
    filtered = df  # Aucun filtre

# filtered = filtered.groupby(['m', 'n', 'k', 'b', 'p', 'q',"P", 'algo', 'lookahead'], as_index=False)['gflops'].mean()
filtered_fig1 = filtered.groupby(['P', 'algo',"n"], as_index=False)['gflops'].mean()
filtered_fig4 = filtered.groupby(['P', 'algo', 'n', "lookahead" ], as_index=False)['gflops'].mean()

filtered_fig2 = filtered.groupby(['n', 'algo'], as_index=False)['gflops'].mean()
filtered_fig3 = filtered.groupby(['n', 'algo','lookahead' ], as_index=False)['gflops'].mean()
# Graph Scalabilité forte : GFLOPS vs nombre de processus
selected_n = st.selectbox("Taille des matrices",filtered_fig1["n"].unique() )
filtered_fig1 = filtered_fig1[filtered_fig1["n"] == selected_n]
filtered_fig4 = filtered_fig4[filtered_fig4["n"] == selected_n]



fig1 = px.line(
    filtered_fig1,
    x="P",
    y="gflops",
    color="algo",
    # line_group="n",
    markers=True,
    labels={"P": "Nombre de processus (P)", "gflops": "GFLOPS"},
    title=f"📈 Scalabilité forte — GFLOPS en fonction du nombre de processus pour matrice de taille : {selected_n}x{selected_n}"
)
fig1.update_layout(legend_title_text='Algorithme')


fig4 = px.line(
    filtered_fig4,
    x="P",
    y="gflops",
    color="algo",
    symbol="lookahead",
    # markers=True,
    labels={"P": "Nombre de processus (P)", "gflops": "GFLOPS"},
    title=f"📈 Scalabilité forte — GFLOPS en fonction du nombre de processus pour matrice de taille : {selected_n}x{selected_n}"
)
fig4.update_layout(legend_title_text='Algorithme')
# Graph Scalabilité forte : GFLOPS vs taille de problème
fig2 = px.line(
    filtered_fig2,
    x="n",
    y="gflops",
    color="algo",
    # symbol="lookahead",
    labels={"n": "Dimension n (taille de la matrice)", "gflops": "GFLOPS"},
    title="📊 Performances selon la taille de la matrice (n)"
)

fig3 = px.line(
    filtered_fig3,
    x="n",
    y="gflops",
    color="algo",
    symbol="lookahead",
    labels={"n": "Dimension n (taille de la matrice)", "gflops": "GFLOPS"},
    title="📊 Performances selon la taille de la matrice (n)"
)

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)

# Table
with st.expander("🔍 Voir les données brutes"):
    st.dataframe(filtered)

