import streamlit as st
from modules.auth import *
from modules.auth_check import load_css

# ================= CONFIG =================
st.set_page_config(page_title="Clustering Analytics", layout="wide")

# ================= LOAD CSS =================
load_css(
    "assets/style/style.css",
    "assets/style/login.css"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= REDIRECT =================
if "user" in st.session_state:
    st.switch_page("pages/3_dashboard.py")

if "mode" not in st.session_state:
    st.session_state.mode = "login"

# ================= LAYOUT =================
col1, col_mid, col2 = st.columns([2.5, 0.1, 1])

# ================= LEFT SIDE =================
with col1:
    st.markdown('<div class="hero">', unsafe_allow_html=True)

    st.markdown('<div class="hero-badge">🚀 Data Intelligence Platform</div>', unsafe_allow_html=True)

    st.markdown('<h1>Clustering Analytics</h1>', unsafe_allow_html=True)

    st.markdown("""
    Platform analisis data penjualan multi e-commerce menggunakan 
    <b>K-Medoids Clustering</b> untuk membantu bisnis memahami:
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-features">
    ✔ Produk terlaris berdasarkan pola pembelian <br>
    ✔ Segmentasi pelanggan & market <br>
    ✔ Insight strategi penjualan berbasis data
    </div>
    """, unsafe_allow_html=True)

    # ======= FAKE CHART (VISUAL ONLY) =======
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">Sales Clustering Insight</div>
        <div class="bars">
            <div class="bar" style="height:70%"></div>
            <div class="bar" style="height:50%"></div>
            <div class="bar" style="height:90%"></div>
            <div class="bar" style="height:60%"></div>
            <div class="bar" style="height:80%"></div>
        </div>
        <div class="chart-labels">
            <span>C1</span><span>C2</span><span>C3</span><span>C4</span><span>C5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<a class="try-btn">🚀 Mulai Sekarang</a>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= DIVIDER =================
with col_mid:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ================= RIGHT SIDE =================
with col2:
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    if st.session_state.mode == "login":

        st.markdown('<div class="auth-title">Login</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Masuk ke akun anda</div>', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="Masukkan email")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")

        if st.button("Login", use_container_width=True):

            if not email or not password:
                st.warning("Semua field wajib diisi!")
            else:
                with st.spinner("Memproses login..."):
                    user = login_user(email, password)

                if user:
                    st.session_state.user = user
                    st.success("Login berhasil!")
                    st.switch_page("pages/3_dashboard.py")
                else:
                    st.error("Email atau password salah!")

        st.markdown("---")

        col_a, col_b = st.columns([2,1])
        with col_a:
            st.write("Belum punya akun?")
        with col_b:
            if st.button("Daftar", key="to_register"):
                st.session_state.mode = "register"
                st.rerun()

    else:
        st.markdown('<div class="auth-title">Register</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Buat akun baru</div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Masukkan username")
        email = st.text_input("Email", placeholder="Masukkan email")
        password = st.text_input("Password", type="password", placeholder="Minimal 8 karakter")
        confirm_password = st.text_input("Konfirmasi Password", type="password")

        if st.button("Daftar", use_container_width=True):
            if not username or not email or not password:
                st.warning("Semua field wajib diisi!")

            elif password != confirm_password:
                st.error("Password tidak sama!")

            else:
                valid, message = is_strong_password(password)

                if not valid:
                    st.error(message)
                else:
                    with st.spinner("Membuat akun..."):
                        success = register_user(username, email, password)

                    if success:
                        st.success("Registrasi berhasil! Silakan login.")
                        st.session_state.mode = "login"
                        st.rerun()
                    else:
                        st.error("Email sudah digunakan!")

        st.markdown("---")

        st.markdown('<div class="switch-text">Sudah punya akun?</div>', unsafe_allow_html=True)

        if st.button("Login", key="to_login"):
            st.session_state.mode = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)