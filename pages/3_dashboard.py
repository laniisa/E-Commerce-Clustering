import streamlit as st
import pandas as pd
import plotly.express as px
from modules.auth_check import *
from components.sidebar import show_sidebar
from modules.daashboard import *
load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/dashboard.css",
)


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("dashboard")


user_id = st.session_state.user["id_user"]
df_history = get_clustering_history(user_id)
user_name = st.session_state.user["username"]

st.title("Dashboard")

st.markdown(f"""
<div class="alert-box">
    <div class="alert-title">Selamat Datang, {user_name} 👋</div>
    <div class="alert-desc">
        Sistem siap membantu Anda melakukan analisis clustering data penjualan menggunakan algoritma K-Medoids,
        melihat riwayat proses analisis, serta menampilkan hasil segmentasi data.
    </div>
</div>
""", unsafe_allow_html=True)

colp1, colp2, colp3 = st.columns([1,5,1])
with colp1:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Panduan Sistem", use_container_width=True):
        st.switch_page("pages/9_panduan.py")

#HISTORY KOSONG

if df_history.empty:
    st.markdown("""
    <div class="empty-box">
        Belum ada riwayat clustering yang tersimpan.<br>
        Silakan lakukan proses clustering data terlebih dahulu.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Mulai Clustering Sekarang", use_container_width=True):
            st.switch_page("pages/4_upload_data.py")
    st.stop()


# SAFE DATA

df_history["silhouette_score"] = pd.to_numeric(df_history["silhouette_score"], errors="coerce").fillna(0)
df_history["dbi_score"] = pd.to_numeric(df_history["dbi_score"], errors="coerce").fillna(0)
df_history["created_at"] = pd.to_datetime(df_history["created_at"], errors="coerce")

summary = get_dashboard_summary(user_id)

total_dataset = summary["total_dataset"]
total_analisis = summary["total_analisis"]
avg_sil = summary["avg_silhouette"]
best_dbi = summary["best_dbi"]

st.markdown("### Overview")

m1,m2,m3,m4 = st.columns(4)

metric_data = [
    ("Total Dataset", total_dataset),
    ("Total Analisis", total_analisis),
    ("Avg Silhouette", avg_sil),
    ("Best DBI Score", best_dbi)
]

for col, item in zip([m1,m2,m3,m4], metric_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{item[0]}</div>
            <div class="metric-value">{item[1]}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()


# HASIL

if "selected_history" not in st.session_state:
    st.session_state.selected_history = df_history.iloc[0]["id"]

if "show_cluster_data" not in st.session_state:
    st.session_state.show_cluster_data = False


selected_df = df_history[
    df_history["id"] == st.session_state.selected_history
]

# jika id tidak ditemukan

if selected_df.empty:
    st.session_state.selected_history = df_history.iloc[0]["id"]
    selected_df = df_history[
        df_history["id"] == st.session_state.selected_history
    ]
selected = selected_df.iloc[0]


left, right= st.columns(2)

# kiri → plot
with left:
    st.markdown("### Clustering Result")
    st.caption(f"Analysis Dataset {selected['dataset_name']} dengan k = {selected['k_cluster']}")
    try: 
        st.image(selected["file_path_plot"], width=520) 
    except: 
        st.warning("Visualisasi cluster tidak ditemukan.")

    left1, left2  = st.columns(2)
    with left1:
        try:
            with open(selected["file_path_result"], "rb") as f:
                st.download_button(
                    ":material/download: Download Hasil",
                    f,
                    file_name=f"cluster-{selected['dataset_name']}.csv",
                    use_container_width=True
                )
        except:
            st.warning("File hasil clustering tidak ditemukan")
    with left2:
        if st.button("Lihat Data Cluster", use_container_width=True):
            st.session_state.show_cluster_data = not st.session_state.show_cluster_data

# kanan → info
with right:
    st.markdown("### Riwayat Analisis")

    if "page" not in st.session_state:
            st.session_state.page = 1

    per_page = 7
    total = len(df_history)
    total_page = (total // per_page) + (1 if total % per_page else 0)

    start = (st.session_state.page - 1) * per_page
    current_data = df_history[start:start + per_page]

    st.markdown("""
    <div class="table-header">
        <div>Tanggal</div>
        <div>Dataset</div>
        <div>K</div>
        <div>Score / DBI</div>
        <div>Aksi</div>
    </div>
    """, unsafe_allow_html=True)

    for row in current_data.itertuples():
        is_active = "history-active" if row.id == st.session_state.selected_history else ""

        col1, col2, col3, col4, col5 = st.columns([2,3,1,2,2])
        tanggal = row.created_at.strftime("%d-%m-%Y")
        
        with col1:
            st.markdown(f'<div class="table-row {is_active}">{tanggal}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="table-row {is_active}">{row.dataset_name}</div>', unsafe_allow_html=True)

        with col3:
            st.markdown(f'<div class="table-row center {is_active}">{row.k_cluster}</div>', unsafe_allow_html=True)

        with col4:
            st.markdown(f'<div class="table-row center {is_active}">{round(row.silhouette_score,3)} / {round(row.dbi_score,3)}</div>', unsafe_allow_html=True)

        with col5:
            h1,h2= st.columns(2)
            with h1:
                if st.button(":material/visibility:", key=f"view_{row.id}"):
                    st.session_state.selected_history = row.id
                    st.session_state.show_cluster_data = False
                    st.rerun()
            with h2:
                if st.button(":material/delete:", key=f"del_{row.id}"):
                    del_analisis(row)

    
    col1, col2, col3 = st.columns([6,1,1])

    with col1:
        st.markdown(f"""
        <div class="page-text">
            Page {st.session_state.page} of {total_page}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("‹", key="prev"):
            if st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()

    with col3:
        if st.button("›", key="next"):
            if st.session_state.page < total_page:
                st.session_state.page += 1
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

     
if st.session_state.show_cluster_data:
    st.divider()
    st.markdown("### Detail Data Hasil Clustering")

    try:
        df_cluster = pd.read_csv(selected["file_path_result"])

        cluster_list = sorted(df_cluster["cluster"].unique())
        tabs = st.tabs([f"Cluster {c}" for c in cluster_list])

        for i, c in enumerate(cluster_list):
            with tabs[i]:

                data_c = df_cluster[df_cluster["cluster"] == c]

                st.caption(f"Jumlah data pada cluster {c} adalah {len(data_c)}")
                st.dataframe(data_c, use_container_width=True, height=350)

                st.markdown(f"""
                <div class="analysis-box">
                <b>Interpretasi Cluster {c}</b><br><br>

                Cluster {c} memiliki jumlah data sebanyak <b>{len(data_c)}</b>. <br>
                Variabel <b>price</b> memiliki nilai mean sebesar <b>{round(data_c["price"].mean(),2)}</b> dan median <b>{round(data_c["price"].median(), 2)}</b>. <br>
                Variabel <b>discount</b> memiliki nilai mean sebesar <b>{round(data_c["discount"].mean(), 2)}</b> dan median <b>{round(data_c["discount"].median(), 2)}</b>. <br>
                Variabel <b>quantity</b> memiliki nilai mean sebesar <b>{round(data_c["quantity"].mean(), 2)}</b> dan median <b>{round(data_c["quantity"].median(), 2)}</b>. <br>
                Variabel <b>total_sales</b> memiliki nilai mean sebesar <b>{round(data_c["total_sales"].mean(), 2)}</b> dan median <b>{round(data_c["total_sales"].median(), 2)}</b>.
                </div>
                """, unsafe_allow_html=True)
    except:
        st.warning("Data hasil clustering tidak dapat dibuka.")

    
st.divider()


# ======================
# ACTION BUTTON
# ======================
col1, col2, col3= st.columns([1,5,1])
with col1:
    if st.button("Panduan Sistem", key="guide_btn", use_container_width=True):
        st.switch_page("pages/9_panduan.py")

with col3:
    if st.button("Mulai Clustering", key="start_btn", use_container_width=True):
        st.switch_page("pages/4_upload_data.py")