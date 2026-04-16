import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io

from sklearn.decomposition import PCA
from modules.auth_check import check_login, load_css
from components.sidebar import show_sidebar
from modules.clustering import *


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

load_css(
    "assets/style/style.css",
    "assets/style/clustering.css"
)
check_login()
show_sidebar("clustering")

# ======================
# LOAD DATA (NORMALIZED)
# ======================
df = st.session_state.get("normalized")
dataset_id = st.session_state.get("active_dataset_id")
user_id = st.session_state.user["id_user"]

st.title("📊 Clustering Analysis")

if df is None:
    st.warning("Silahkan lakukan preprocessing terlebih dahulu!")
    st.stop()

st.caption("K-Medoids Clustering untuk Analisis Pola Penjualan")

# ======================
# CONTROL PANEL
# ======================
st.markdown("### ⚙️ Konfigurasi Clustering")

col1, col2, col3 = st.columns([2,1,1])

with col1:
    selected_cols = st.multiselect(
        "Pilih fitur",
        ["price", "discount", "quantity", "total_sales"],
        default=["price", "discount", "quantity", "total_sales"]
    )
    if len(selected_cols) < 2:
        st.warning("Minimal 2 fitur")
        st.stop()

    X = df[selected_cols]

with col2:
    method = st.selectbox("Metode K", ["Manual", "Otomatis"])

with col3:
    if method == "Manual":
        k = st.number_input("Jumlah K", 2, 10, 3)
    if method == "Otomatis":
        best_k, scores = find_best_k(X)

        # simpan ke session
        st.session_state.best_k = best_k
        st.session_state.silhouette_scores = scores

        # ======================
        # TAMPILKAN GRAFIK
        # ======================
        if "silhouette_scores" in st.session_state:

            scores = st.session_state.silhouette_scores
            best_k = st.session_state.best_k

            st.markdown("### 📈 Silhouette Score vs K")

            df_score = pd.DataFrame({
                "k": list(scores.keys()),
                "score": list(scores.values())
            })

            fig = px.line(
                df_score,
                x="k",
                y="score",
                markers=True,
                title="Silhouette Score"
            )

            # highlight best k
            fig.add_scatter(
                x=[best_k],
                y=[scores[best_k]],
                mode="markers",
                marker=dict(size=12, color="red"),
                name=f"Best K = {best_k}"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.success(f"✅ K optimal berdasarkan Silhouette Score adalah: **{best_k}**")


# ======================
# BUTTON
# ======================
if st.button("Proses Clustering", use_container_width=True):
    if method == "Otomatis":
        if "best_k" not in st.session_state:
            st.warning("Silakan cari K optimal dulu!")
            st.stop()
        k = st.session_state.best_k

    labels, model = run_kmedoids(X, int(k))


    df_clustered = attach_cluster(df, labels)
    eval_result = evaluate_clustering(X, labels)

    st.session_state.clustered = df_clustered
    st.session_state.eval = eval_result
    st.session_state.model = model
    st.session_state.X = X


# ======================
# RESULT SECTION
# ======================
if "clustered" in st.session_state:

    dfc = st.session_state.clustered
    eval_result = st.session_state.eval
    model = st.session_state.get("model")
    X = st.session_state.get("X")

    st.markdown("---")
    st.markdown("## 📊 Clustering Result")

    # ======================
    # LAYOUT: GRAPH + METRIC
    # ======================
    col1, col2 = st.columns([2.5,1.5])

    with col1:
        tab1, tab2 = st.tabs(["Diagram", "Summary"])
        with tab1:
            st.markdown("### Visualisasi")
        
            selected_platform = st.selectbox(
                "Pilih Platform",
                ["Semua"] + list(dfc["platform"].unique())
            )

            if selected_platform != "Semua":
                df_filtered = dfc[dfc["platform"] == selected_platform]
            else:
                df_filtered = dfc
            
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)

            dfc["PC1"] = X_pca[:, 0]
            dfc["PC2"] = X_pca[:, 1]

            fig = px.scatter(
                dfc,
                x="PC1",
                y="PC2",
                color="cluster",
                title="Clustering Visualization (PCA)"
            )

            medoids = model.cluster_centers_
            medoids_pca = pca.transform(medoids)

            fig.add_scatter(
                x=medoids_pca[:, 0],
                y=medoids_pca[:, 1],
                mode="markers",
                marker=dict(size=14, color="red", symbol="x"),
                name="Medoid"
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 📋 Ringkasan Cluster")

            summary = get_cluster_summary(dfc)
            labels_map = label_cluster(summary)
            summary["label"] = summary["cluster"].map(labels_map)

            st.dataframe(summary, use_container_width=True)

        # ======================
        # SAVE
        # ======================
        if st.button("💾 Simpan Hasil"):
            if "clustered" not in st.session_state:
                st.error("Belum ada hasil clustering!")
                st.stop()

            df_cluster = st.session_state.clustered

            file_csv = save_cluster_csv(df_cluster, dataset_id)
            file_plot = save_plot(df_cluster, dataset_id)

            save_summary(
                dataset_id,
                user_id,
                k,
                method,
                st.session_state.eval["Silhouette"],
                st.session_state.eval["DBI"],
                file_csv,
                file_plot
            )

            st.success("Hasil berhasil disimpan")

    with col2:
        st.markdown("### 📌 Evaluation")
        colA, colB = st.columns(2)
        with colA:
            st.metric("Silhouette Score", round(eval_result["Silhouette"], 3))
        with colB:
            st.metric("Davies-Bouldin Index (DBI)", round(eval_result["DBI"], 3))

        
        # ======================
            # DISTRIBUSI CLUSTER
            # ======================
        st.markdown("### 📦 Distribusi Cluster")

        cluster_count = (
            dfc["cluster"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        cluster_count.columns = ["cluster", "jumlah"]

        st.plotly_chart(
            px.bar(cluster_count, x="cluster", y="jumlah", color="cluster"),
            use_container_width=True
        )
    st.divider()
    # ======================
    # TAB PER CLUSTER
    # ======================
    st.markdown("### 📂 Detail per Cluster")

    cluster_list = sorted(dfc["cluster"].unique())
    tabs = st.tabs([f"Cluster {c}" for c in cluster_list])

    for i, c in enumerate(cluster_list):
        with tabs[i]:
            data_c = dfc[dfc["cluster"] == c]
            st.dataframe(data_c, use_container_width=True)
            st.caption(f"Jumlah data: {len(data_c)}")

    st.divider()

    # ======================
    # INSIGHT
    # ======================
    st.markdown("### 🧠 Insight")

    insights = generate_insight(summary, labels_map)

    for ins in insights:
        st.success(ins)

    st.divider()
            
    col1, col2, col3 = st.columns([1, 6 ,1])

    with col1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.switch_page("pages/6_eda.py")
    with col3:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dfc.to_excel(writer, index=False, sheet_name='Data')
            summary.to_excel(writer, index=False, sheet_name='Summary')

        st.download_button(
            "Download Excel",
            output.getvalue(),
            "hasil_clustering.xlsx"
        )
