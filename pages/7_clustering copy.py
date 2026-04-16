import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io

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

st.title("📊 Clustering (K-Medoids)")

# ======================
# LOAD DATA (NORMALIZED)
# ======================
df = st.session_state.get("normalized")
dataset_id = st.session_state.get("active_dataset_id")
user_id = st.session_state.user["id_user"]

if df is None:
    st.warning("Silahkan lakukan preprocessing terlebih dahulu!")
    st.stop()

# ======================
# PREPARE DATA
# ======================
col1, col2 = st.columns(2)
with col1:
    all_num_cols = ["price", "discount", "quantity", "total_sales"]

    selected_cols = st.multiselect(
        "Pilih fitur untuk clustering",
        options=all_num_cols,
        default=all_num_cols
    )

    if len(selected_cols) < 2:
        st.warning("Minimal pilih 2 fitur")
        st.stop()
with col2:
    X = df[selected_cols]

    col1, col2 = st.columns(2)
    col1.metric("Jumlah Data", X.shape[0])
    col2.metric("Jumlah Fitur", X.shape[1])

st.divider()
# ======================
# PILIH METODE K
# ======================
st.subheader(" Penentuan Jumlah Cluster")

method = st.radio(
    "Pilih metode penentuan K:",
    ["Manual", "Otomatis (Silhouette Score)"]
)
# ======================
# AUTO K
# ======================
if method == "Otomatis (Silhouette Score)":
    if st.button("Cari K "):
        best_k, scores = find_best_k(X)

        st.session_state.best_k = best_k
        st.session_state.scores = scores

    if "scores" in st.session_state:
        st.subheader("Visualisasi Silhouette Score")
        scores = st.session_state.scores

        fig = px.line(
            x=list(scores.keys()),
            y=list(scores.values()),
            markers=True,
            title="Silhouette Score nilai K"
        )
        st.plotly_chart(fig)

        st.success(f"K optimal berdasarkan Silhouette Score adalah: {st.session_state.best_k}")

    k = st.session_state.get("best_k", 2)

else:
    k = st.number_input("Masukkan jumlah cluster (K):", min_value=2, max_value=12, value=3)

st.divider()
# ======================
# CLUSTERING
# ======================
if st.button("Jalankan Clustering"):
    labels, model = run_kmedoids(X, int(k))
    df_clustered = attach_cluster(df, labels)
    eval_result = evaluate_clustering(X, labels)
    sill_result = evaluate_clustering(X, labels)

    st.session_state.clustered = df_clustered
    st.session_state.eval = eval_result
    st.session_state.sill = sill_result


# ======================
# HASIL
# ======================
if "clustered" in st.session_state:

    dfc = st.session_state.clustered
    eval_result = st.session_state.eval

    st.subheader("📊 Hasil Clustering")

    col1, col2 = st.columns(2)
    col1.metric("DBI", round(eval_result["DBI"], 4))
    col2.metric("Silhouette", round(eval_result["Silhouette"], 4))

    # ======================
    # DISTRIBUSI CLUSTER
    # ======================
    st.subheader("📦 Distribusi Cluster & Detail Data")

    # Urutkan cluster
    cluster_count = (
        dfc["cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_count.columns = ["cluster", "jumlah_data"]

    # Tampilkan ringkasan
    for row in cluster_count.itertuples():
        st.write(f"Cluster {row.cluster} : {row.jumlah_data} data")

    st.divider()
    # ======================
    # TAB PER CLUSTER
    # ======================
    st.subheader("📂 Detail Data per Cluster")

    cluster_list = sorted(dfc["cluster"].unique())
    tabs = st.tabs([f"Cluster {c}" for c in cluster_list])

    for i, c in enumerate(cluster_list):
        with tabs[i]:
            st.markdown(f"### Data Cluster {c}")

            df_cluster_i = dfc[dfc["cluster"] == c]

            st.dataframe(df_cluster_i)

            st.write(f"Jumlah data: {len(df_cluster_i)}")
    st.divider()

    # ======================
    # FILTER PLATFORM
    # ======================
    st.subheader("🔎 Filter Berdasarkan Platform")

    selected_platform = st.selectbox(
        "Pilih Platform",
        ["Semua"] + list(dfc["platform"].unique())
    )

    if selected_platform != "Semua":
        df_filtered = dfc[dfc["platform"] == selected_platform]
    else:
        df_filtered = dfc

    # ======================
    # VISUAL SCATTER
    # ======================
    st.subheader("📊 Visualisasi Cluster")

    fig = px.scatter(
        df_filtered,
        x="price",
        y="total_sales",
        color="cluster",
        size="quantity",
        hover_data=["product_category"]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    # ======================
    # SUMMARY
    # ======================
    summary = get_cluster_summary(dfc)
    labels_map = label_cluster(summary)
    summary["label"] = summary["cluster"].map(labels_map)

    st.subheader("📋 Ringkasan Cluster")
    st.dataframe(summary)

    # BAR
    fig_bar = px.bar(
        summary,
        x="cluster",
        y="total_data",
        color="label",
        title="Jumlah Data per Cluster"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ======================
    # INSIGHT
    # ======================
    st.subheader("🧠 Insight Cluster")

    insights = generate_insight(summary, labels_map)

    for ins in insights:
        st.info(ins)
    
    st.divider()

    # ======================
    # PER PLATFORM
    # ======================
    st.subheader("📊 Distribusi Cluster per Platform")

    cp = dfc.groupby(["platform", "cluster"]).size().reset_index(name="jumlah")

    fig_cp = px.bar(
        cp,
        x="platform",
        y="jumlah",
        color="cluster",
        barmode="group"
    )
    st.plotly_chart(fig_cp)

    # ======================
    # DOWNLOAD EXCEL
    # ======================
    st.subheader("⬇️ Download Hasil")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dfc.to_excel(writer, index=False, sheet_name='Clustering')
        summary.to_excel(writer, index=False, sheet_name='Summary')

    st.download_button(
        label="Download Excel",
        data=output.getvalue(),
        file_name="hasil_clustering.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()
# ======================
# HASIL
# ======================
if "clustered" in st.session_state:
    st.write("### 📊 Hasil Clustering")
    st.dataframe(st.session_state.clustered.head())

    st.write("### 📌 Evaluasi")
    st.json(st.session_state.eval)

    # ======================
    # VISUALISASI
    # ======================
    st.write("### 📉 Visualisasi Cluster")

    fig, ax = plt.subplots()
    scatter = ax.scatter(
        st.session_state.clustered["price"],
        st.session_state.clustered["total_sales"],
        c=st.session_state.clustered["cluster"]
    )
    ax.set_xlabel("Price")
    ax.set_ylabel("Total Sales")
    st.pyplot(fig)

# ======================
# SAVE
# ======================
if st.button("💾 Simpan Hasil"):
    if "clustered" not in st.session_state:
        st.error("Belum ada hasil clustering!")
        st.stop()

    if user_id is None:
        st.error("User tidak terdeteksi. Silakan login ulang!")
        st.stop()

    df_cluster = st.session_state.clustered

    file_csv = save_cluster_csv(df_cluster, dataset_id)
    file_plot = save_plot(df_cluster, dataset_id)

    save_summary(
        dataset_id,
        user_id,
        k,
        method,
        st.session_state.sill["Silhouette"],
        st.session_state.eval["DBI"],
        file_csv,
        file_plot
    )

    st.success("Hasil berhasil disimpan")

    # ======================
    # DOWNLOAD
    # ======================
    csv = st.session_state.clustered.to_csv(index=False).encode('utf-8')

    
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("⬅️ Kembali", use_container_width=True):
        st.switch_page("pages/6_eda.py")
with col_btn2:
        st.download_button(
            "⬇️ Download Hasil Clustering",
            csv,
            "hasil_clustering.csv",
            "text/csv"
        )

