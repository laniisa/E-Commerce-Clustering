import streamlit as st
from modules.auth_check import load_css


st.set_page_config(
    page_title="Clustering Analytics",
    layout="wide"
)
load_css("assets/style/app.css")

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
[data-testid="stSidebarNav"] {display:none;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


nav1, nav2, nav3 = st.columns([3,4,2])
with nav1:
    logo1, logo2 = st.columns([1,5])
    with logo1:
        st.image("assets/image/clustering_icon.jpg",width=45)
    with logo2:
        st.markdown("""<div class="logo-text">Clustering Analytics</div>""", unsafe_allow_html=True)
with nav3:
    colbtn1, colbtn2 = st.columns(2)
    with colbtn2:
        if st.button("Sign In", use_container_width=True):
            st.switch_page("pages/1_login.py")

left, right = st.columns([1.3, 1], gap="large")
with left:
    st.markdown("""
    <div class="hero-title1">Analisis Data Penjualan</div>
    <div class="hero-title2">Berbasis EDA & K-Medoids</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-desc">
        Platform analisis data penjualan multi-platform e-commerce ( Shopee, Lazada, dan TiktokShop)
        untuk membantu pelaku usaha memahami tren historis penjualan,
        performa produk, dan segmentasi produk menggunakan pendekatan
        <b>EDA</b> dan <b>K-Medoids Clustering</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-list">
        <div>✔ Visualisasi Data Penjualan</div>
        <div>✔ Clustering K-Medoids</div>
        <div>✔ Analisis Multi Platform</div>
        <div>✔ Insight Berbasis Data</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1,col2 = st.columns([1,4])
    with col1:
        if st.button("Get Started", use_container_width=True):
            st.switch_page("pages/1_login.py")

with right:
    st.markdown('<div class="hero-image">', unsafe_allow_html=True)
    st.image("assets/image/data-analiysis.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-title">
    Fitur Utama
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Exploratory Data Analysis</div>
        <div class="feature-desc">
            Menampilkan statistik deskriptif,
            distribusi data, visualisasi tren penjualan,
            dan performa penjualan antar platform.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧩</div>
        <div class="feature-title">K-Medoids Clustering</div>
        <div class="feature-desc">
            Mengelompokkan produk berdasarkan
            karakteristik penjualan sehingga menghasilkan
            segmentasi produk yang lebih terstruktur.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📁</div>
        <div class="feature-title">Riwayat Analisis</div>
        <div class="feature-desc">
            Menyimpan hasil clustering dan visualisasi
            data sehingga dapat diakses kembali kapan saja.
        </div>
    </div>
    """, unsafe_allow_html=True)


# WORKFLOW

st.markdown("""
<div class="section-title">
    Alur Penggunaan Sistem
</div>
""", unsafe_allow_html=True)

workflow1, workflow2, workflow3, workflow4, workflow5 = st.columns(5)

steps = [
    ("1", "Upload Dataset"),
    ("2", "EDA & Visualisasi"),
    ("3", "Preprocessing"),
    ("4", "K-Medoids"),
    ("5", "Interpretasi")
]

for col, step in zip(
    [workflow1, workflow2, workflow3, workflow4, workflow5],
    steps
):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-number">{step[0]}</div>
            <div class="step-text">{step[1]}</div>
        </div>
        """, unsafe_allow_html=True)
        
# FOOTER

st.markdown("""
<div class="footer">
    Sistem Analisis Clustering berbasis K-Medoids • @2026
</div>
""", unsafe_allow_html=True)