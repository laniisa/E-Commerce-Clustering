import streamlit as st
import pandas as pd
from modules.auth_check import check_login
from components.sidebar import show_sidebar
from components.header import *
from modules.daashboard import get_clustering_history

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("history")

import streamlit as st
import numpy as np
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score

st.title("📊 Clustering K-Medoids")

X_scaled = st.session_state.get("X_scaled")

if X_scaled is None:
    st.warning("Lakukan preprocessing dulu!")
    st.stop()

k_range = range(2, 9)

sil_scores = []

for k in k_range:
    model = KMedoids(
        n_clusters=k,
        metric="euclidean",
        init="k-medoids++",
        method="alternate",
        random_state=42
    )
    labels = model.fit_predict(X_scaled)
    sil_scores.append(silhouette_score(X_scaled, labels))

best_k = k_range[np.argmax(sil_scores)]

st.write("Best k:", best_k)

# FINAL MODEL
model = KMedoids(
    n_clusters=best_k,
    metric="euclidean",
    init="k-medoids++",
    method="alternate",
    random_state=42
)
labels = model.fit_predict(X_scaled)

st.success("Clustering selesai!")
