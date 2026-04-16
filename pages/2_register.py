import streamlit as st
from modules.auth import register_user, is_strong_password
from modules.auth_check import load_css

load_css(
    "assets/style/style.css",
    "assets/style/login.css"
)
# hide sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📝 Register</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    st.markdown('<div class="auth-title">📝 Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Mulai analisis data penjualan</div>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Masukkan username")
    email = st.text_input("Email", placeholder="Masukkan email")
    password = st.text_input("Password", type="password", placeholder="Minimal 8 karakter")
    confirm_password = st.text_input("Konfirmasi Password", type="password")

    # ======================
    # REGISTER BUTTON
    # ======================
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
                    st.switch_page("pages/1_Login.py")
                else:
                    st.error("Email sudah digunakan!")

    st.markdown("---")

    if st.button("⬅ Kembali ke Login", use_container_width=True):
        st.switch_page("pages/1_Login.py")

    st.markdown('</div>', unsafe_allow_html=True)