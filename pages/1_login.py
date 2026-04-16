import streamlit as st
from modules.auth import *
from modules.auth_check import load_css

load_css(
    "assets/style/style.css",
    "assets/style/login.css"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}

</style>
""", unsafe_allow_html=True)

if "user" in st.session_state:
    st.switch_page("pages/3_dashboard.py")

if "mode" not in st.session_state:
    st.session_state.mode = "login"

col1, col_mid, col2= st.columns([2.5, 0.05, 1])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4149/4149653.png", width=100)

    st.markdown('<div class="left-title">Clustering Analytics</div>', unsafe_allow_html=True)

    st.markdown("""
    Platform analisis data penjualan multi e-commerce menggunakan metode K-Medoids 
    untuk membantu menemukan pola produk terlaris, segmentasi pasar, dan insight bisnis.
    """)

    st.markdown("""
    ✔ Analisis otomatis  
    ✔ Visualisasi interaktif  
    ✔ Insight bisnis  
    """)

    st.markdown('<a class="try-btn">🚀 Try Now</a>', unsafe_allow_html=True)


with col_mid:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with col2:
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
        st.markdown('<h2>Register</h2>', unsafe_allow_html=True)
        st.caption("Create Account")

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
                    if register_user(username, email, password):
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