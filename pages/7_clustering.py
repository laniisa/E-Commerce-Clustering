import streamlit as st
import pandas as pd
import plotly.express as px
import io

from modules.auth_check import *
from components.sidebar import show_sidebar
from modules.clustering import *

load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/clustering.css"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
.block-container{
    padding-top:1.2rem;
}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("clustering")


df_transform = st.session_state.get("data_ready")
df_original = st.session_state.get("data_original")
dataset_id = st.session_state.get("active_dataset_id")
user_id = st.session_state.user["id_user"]

st.title("Clustering Analysis")
st.markdown(f"""
<div class="alert-box">
    <div class="alert-desc">
        Analisis clustering data penjualan menggunakan algoritma K-Medoids <br> Proses clustering dilakukan terhadap data transaksi penjualan menggunakan variabel numerik berupa price, discount, quantity, dan total_sales untuk mengelompokkan pola transaksi yang memiliki karakteristik serupa.
    </div>
</div>
""", unsafe_allow_html=True)

if df_transform is None:
    st.warning("Silakan lakukan EDA terlebih dahulu!")
    st.stop()


st.markdown("### Konfigurasi Clustering")
c1, c2, c3 = st.columns([2,1,1])
with c1:
    selected_cols = st.multiselect(
        "Pilih fitur clustering",
        ["price","discount","quantity","total_sales"],
        default=["price","discount","quantity","total_sales"]
    )
    if len(selected_cols) < 2:
        st.warning("Minimal pilih 2 fitur")
        st.stop()

X = cols_cluster(df_transform[selected_cols])
st.session_state.X = X
st.session_state.selected_cols = selected_cols

with c2:
    method = st.selectbox("Metode Penentuan K", ["Silhouette Score", "Manual"])
with c3:
    if method == "Manual":
        k = st.number_input("Jumlah Cluster", min_value=2, max_value=10, value=3)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Cari K Optimal", use_container_width=True):
            with st.spinner("Menghitung silhouette score..."):
                best_k, scores = silhouette_scores(X)
            st.session_state.best_k = best_k
            st.session_state.silhouette_scores = scores


# SILHOUETTE 

if "silhouette_scores" in st.session_state and st.session_state.silhouette_scores:
    scores = st.session_state.silhouette_scores
    best_k = st.session_state.best_k

    st.markdown("### Silhouette Score")
    df_score = pd.DataFrame({
        "k": list(scores.keys()),
        "score": list(scores.values())
    }).sort_values("k")

    fig = px.line(
        df_score,
        x="k",
        y="score",
        markers=True,
        title="Silhouette Score"
    )

    fig.add_scatter(
        x=[best_k],
        y=[scores[best_k]],
        mode="markers",
        marker=dict(size=12, color="red"),
        name=f"Best K = {best_k}"
    )
    st.plotly_chart(fig, use_container_width=True, key="pca_sill")
    st.success(f"Jumlah cluster optimal berdasarkan Silhouette Score adalah K = {best_k}")


# CLUSTERING

if st.button("Proses Clustering", use_container_width=True):

    if method == "Manual":
        k_used = int(k)
    else:
        if "best_k" not in st.session_state or st.session_state.best_k is None:
            st.warning("Cari K optimal terlebih dahulu")
            st.stop()
        k_used = int(st.session_state.best_k)

    labels, model = run_kmedoids(X, k_used)

    st.session_state.clustered = attach_cluster(df_original, labels)
    st.session_state.eval = evaluate_clustering(X, labels)
    st.session_state.model = model
    st.session_state.k_used = k_used


# HASIL

if "clustered" in st.session_state:

    dfc = st.session_state.clustered
    evals = st.session_state.eval
        
    st.divider()
    st.markdown("### Evaluasi Clustering")
    m1,m2,m3,m4 = st.columns(4)
    cards = [
        ("Silhouette Score", round(evals["Silhouette"],3)),
        ("DBI", round(evals["DBI"],3)),
        ("Jumlah Cluster", st.session_state.k_used),
        ("Jumlah Data", len(dfc))
    ]
    for col, item in zip([m1,m2,m3,m4], cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{item[0]}</div>
                <div class="metric-value">{item[1]}</div>
            </div>
            """, unsafe_allow_html=True)

    eval_text = generate_cluster_evaluation(evals, st.session_state.k_used)
    st.markdown(f"""<div class="analysis-box">{eval_text}</div>""", unsafe_allow_html=True)
    
    st.divider()

#FILTER PLATFORM

    st.markdown("## Hasil Clustering")
    selected_platform = st.multiselect(
        "Pilih Platform Analisis",
        options=dfc["platform"].unique(),
        default=dfc["platform"].unique()
    )
    df_view = dfc[dfc["platform"].isin(selected_platform)]
    X_view = st.session_state.X.loc[df_view.index]
    summary = get_cluster_summary(df_view, st.session_state.selected_cols)

    st.divider()
    #VISUALISASI
    vis1, vis2 = st.columns(2)
    with vis1:    
        st.markdown("### Visualisasi Persebaran Cluster (PCA)")
        st.info("Visualisasi persebaran data hasil clustering menggunakan reduksi dimensi PCA ke dalam dua komponen utama.")
        fig_vis = create_cluster_plot(df_view, X_view)
        st.plotly_chart(fig_vis, use_container_width=True, key="pca_vis")
    #DISTRIBUSI
    with vis2:
        st.markdown("### Distribusi Data per Cluster")
        st.info("Menampilkan jumlah data pada masing-masing cluster untuk melihat keseimbangan distribusi hasil clustering.")
        cluster_dist = df_view["cluster"].value_counts().sort_index().reset_index()
        cluster_dist.columns = ["cluster","jumlah"]
        fig_dist = px.bar(
            cluster_dist, 
            x="cluster", 
            y="jumlah", 
            color="cluster"
        )
        st.plotly_chart(fig_dist, use_container_width=True, key="pca_dist")
 
    st.divider()

    # DETAIL DATA PER CLUSTER

    st.markdown("### Detail Data dan Interpretasi per Cluster")
    st.info("Informasi mengenai karakteristik setiap cluster berdasarkan nilai variabel dan dominasi data di dalamnya.")
    cluster_list = sorted(df_view["cluster"].unique())
    
    tabs = st.tabs([f"Cluster {c}" for c in cluster_list])

    for i, c in enumerate(cluster_list):
        with tabs[i]:

            data_c = df_view[df_view["cluster"] == c]
            dom_platform = data_c["platform"].mode()[0]

            dom_product = data_c["product_name"].mode()[0]

            st.caption(f"Jumlah data pada cluster {c} adalah {len(data_c)}")
            st.dataframe(data_c, use_container_width=True, height=350)

            feature_text = ""

            for col in st.session_state.selected_cols:
                    
                mean_val = round(data_c[col].mean(), 2)
                med_val = round(data_c[col].median(), 2)

                feature_text += (f"""
                Variabel {col} memiliki nilai mean sebesar {mean_val} dan median {med_val}.
                """)

            st.markdown(f"""
            <b>Interpretasi Cluster {c}</b><br><br>

            Cluster {c} memiliki jumlah data sebanyak <b>{len(data_c)}</b>. <br>
            {feature_text}

            Platform dominan pada cluster ini adalah <b>{dom_platform}</b>.

            Kategori produk dominan adalah <b>{dom_product}</b>.

            
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # PAIRPLOT MATRIX
    
    st.markdown("### Scatter Matrix Antar Variabel")
    st.info("Visualisasi hubungan antar variabel pada setiap cluster untuk membantu memahami pola dan pemisahan data.")
    scatter = scatter_matrix_cluster(df_view, st.session_state.selected_cols)

    fig_scat = px.scatter_matrix(
        scatter,
        dimensions= st.session_state.selected_cols,
        color="cluster",
        title="Scatter Matrikx Antar Variabel"
    )
    st.plotly_chart(fig_scat, use_container_width=True, height=700, key="pca_scat")

    st.divider()
    #DATA MEDOID
    st.markdown("## Data Medoid")
    st.info("Data medoid merupakan representasi pusat cluster yang dipilih langsung dari data aktual pada algoritma K-Medoids.")
    medoid = st.session_state.model.medoid_indices_
    medoid_df = df_view.iloc[medoid]
    st.dataframe(medoid_df, use_container_width=True)
    
    # product DOMINAN
    st.markdown("### Dominasi Kategori Produk")
    st.info("Menampilkan kategori produk yang paling dominan pada masing-masing cluster.")
    tab1, tab2 = st.tabs(["Visualisasi", "Data"])
    with tab1:
        cat_df = product_cluster(df_view)

        fig_cat = px.bar(
            cat_df,
            x="cluster",
            y="jumlah",
            color="product_name",
            barmode="group"
        )
        st.plotly_chart(fig_cat, use_container_width=True, key="pca_cat")
    with tab2:
        st.dataframe(cat_df)

    st.divider()

    sav1, sav2, sav3= st.columns([2,4,2])
    with sav1:
        if st.button("Simpan Hasil ", use_container_width=True):

            file_csv = save_cluster_csv(dfc, dataset_id)
            _, file_plot = create_cluster_plot(
                df=dfc,
                X=st.session_state.X,
                dataset_id=dataset_id,
                save=True
            )
            save_summary(
                dataset_id=dataset_id,
                user_id=user_id,
                k_used=st.session_state.k_used,
                method=method,
                silhouette=evals["Silhouette"],
                dbi=evals["DBI"],
                file_csv=file_csv,
                file_plot=file_plot
            )

            st.success("Hasil berhasil disimpan")
    with sav3:
        df_download = dfc[
            dfc["platform"].isin(selected_platform)
        ]

        summary_download = get_cluster_summary(
            df_download,
            st.session_state.selected_cols
        )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_download.to_excel(writer, index=False, sheet_name="Data Cluster")
            summary_download.to_excel(writer, index=False, sheet_name="Summary")
            # sheet evaluation
            eval_df = pd.DataFrame({
                "Metric": [
                    "Silhouette Score",
                    "Davies Bouldin Index",
                    "Jumlah Cluster"
                ],
                "Value": [
                    round(evals["Silhouette"], 3),
                    round(evals["DBI"], 3),
                    st.session_state.k_used
                ]
            })

            eval_df.to_excel(
                writer,
                index=False,
                sheet_name="Evaluation"
            )
        output.seek(0)
        st.download_button(
            "Download ",
            data=output,
            file_name="hasil_clustering.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
