import streamlit as st
from modules.auth import *
from modules.auth_check import load_css

st.set_page_config(page_title="Clustering Analytics", layout="centered")

load_css("assets/style/auth.css")

# hide sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# redirect
if "user" in st.session_state:
    st.switch_page("pages/3_dashboard.py")


# ===== HEADER =====
st.markdown('<div class="login-page">', unsafe_allow_html=True)

st.markdown("""
<h1 class='main-title'>Clustering Analytics</h1>
<p class='subtitle'>K-Medoids Multi Platform Analysis</p>
""", unsafe_allow_html=True)




st.markdown("<h3 class='form-title'>Register</h3>", unsafe_allow_html=True)

username = st.text_input("Username", placeholder="username")
email = st.text_input("Email", placeholder="you@email.com")
password = st.text_input("Password", type="password")
confirm = st.text_input("Konfirmasi Password", type="password")

if st.button("Sign up", use_container_width=True):
    if not username or not email or not password:
        st.warning("Semua field wajib diisi!")
    elif password != confirm:
        st.error("Password tidak sama!")
    else:
        valid, msg = is_strong_password(password)
        if not valid:
            st.error(msg)
        else:
            if register_user(username, email, password):
                st.success("Registrasi berhasil!")
                st.rerun()
            else:
                st.error("Email sudah digunakan!")

st.markdown("<div class='divider'>or</div>", unsafe_allow_html=True)

st.markdown("<div class='switch-center'>Already have an account?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1.8,3])

with col2:
    if st.button("Sign in", key="to_login"):
        st.switch_page("pages/1_login.py")
        st.rerun()
        
st.markdown('</div>', unsafe_allow_html=True)