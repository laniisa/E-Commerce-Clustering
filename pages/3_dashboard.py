import streamlit as st
import pandas as pd
import plotly.express as px
from modules.auth_check import check_login, load_css
from components.sidebar import show_sidebar
from components.header import *
from modules.daashboard import get_clustering_history

load_css(
    "assets/style/style.css",
    "assets/style/dashboard.css"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("dashboard")


st.markdown('<div class="page-title">🏠 Dashboard</div>', unsafe_allow_html=True)

st.markdown("""
<div class="alert-box">
Selamat datang di sistem clustering!
</div>
""", unsafe_allow_html=True)
st.write("Sistem analisis data penjualan mennggunakan K-Medoids")

if st.button ("Lihat Panduan"):
    st.switch_page("pages/9_guide.py")

user_id = st.session_state.user["id_user"]
df_history = get_clustering_history(user_id)


if df_history.empty:
    st.info("Belum ada riwayat clustering.")
    st.stop()
# ======================
# SUMMARY METRICS
# ======================
st.markdown("### 📊 Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📁 Total Dataset", df_history["dataset_name"].nunique())
col2.metric("📊 Total Analisis", len(df_history))
col3.metric("📈 Silhouette (avg)", round(df_history["dbi_score"].mean(), 3))  # bisa ganti nanti
col4.metric("📉 DBI Score", round(df_history["dbi_score"].min(), 3))

st.divider()

# ======================
# RECENT RESULT
# ======================
if "selected_history" not in st.session_state:
    st.session_state.selected_history = df_history.iloc[0]["id"]
    
left, right= st.columns(2)

# kiri → plot
with left:
    selected_id = st.session_state.selected_history 
    selected = df_history[df_history["id"] == selected_id].iloc[0]

    st.markdown("### 📌 Recent Clustering Result")
    st.caption(f"Analysis Dataset {selected['dataset_name']} dengan k = {selected['k_cluster']}")

    try: 
        st.image(selected["file_path_plot"]) 
    except: 
        st.warning("Plot tidak ditemukan")

    try:
        with open(selected["file_path_result"], "rb") as f:
            st.download_button(
                "⬇️ Download Hasil",
                f,
                file_name=f"cluster-{selected['dataset_name']}.csv"
            )
    except:
        st.warning("File tidak ditemukan")

# kanan → info
with right:
    st.markdown("### 📋 Analysis History")

    df_history["created_at"] = pd.to_datetime(df_history["created_at"], errors="coerce")

    if "page" not in st.session_state:
            st.session_state.page = 1

    per_page = 4
    total = len(df_history)
    total_page = (total // per_page) + (1 if total % per_page else 0)

    start = (st.session_state.page - 1) * per_page
    current_data = df_history[start:start + per_page]

    # tampilkan tabel
    df_show = current_data.copy()
    df_show["created_at"] = df_show["created_at"].dt.strftime("%d-%m-%Y")

    # ======================
    # TABLE INTERAKTIF
    # ======================
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

        col1, col2, col3, col4, col5 = st.columns([2,3,1,2,1])

        tanggal = row.created_at.strftime("%d-%m-%Y")
        dbi_color = "green" if row.dbi_score < 0.5 else "red"

        is_active = row.id == st.session_state.selected_history
        bg = "#fce7f3" if is_active else "transparent"
        
        with col1:
            st.markdown(f"""
            <div class="table-row">{tanggal}</div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="table-row">📁 {row.dataset_name}</div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="table-row center">{row.k_cluster}</div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="table-row center">
                {round(row.silhouette_score,3)} / {round(row.dbi_score, 3)} 
            </div>
            """, unsafe_allow_html=True)

        with col5:
            if st.button("🔍", key=f"view_{row.id}"):
                st.session_state.selected_history = row.id
                st.rerun()

    st.markdown('<div class="pagination">', unsafe_allow_html=True)

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
        
st.divider()


# ======================
# ACTION BUTTON
# ======================
col1, col2, col3= st.columns([1,5,1])
with col1:
    if st.button("Panduan", use_container_width=True):
        st.switch_page("pages/9_guide.py")

with col3:
    if st.button("Mulai Clustering", use_container_width=True):
        st.switch_page("pages/4_upload_data.py")
