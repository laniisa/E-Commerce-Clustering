import streamlit as st
from modules.auth import *
from modules.auth_check import load_css

st.set_page_config(page_title="Clustering Analytics", layout="centered")

load_css("assets/style/auth.css")

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# redirect
if "user" in st.session_state:
    role = st.session_state.user.get("role", "user")

    if role == "admin":
        st.switch_page("pages/10_admin_dashboard.py")
    else:
        st.switch_page("pages/3_dashboard.py")


if "mode" not in st.session_state:
    st.session_state.mode = "login"

# ===== HEADER =====
st.markdown('<div class="login-page">', unsafe_allow_html=True)

st.markdown("""
<h1 class='main-title'>Clustering Analytics</h1>
<p class='subtitle'>K-Medoids Multi Platform Analysis</p>
""", unsafe_allow_html=True)


st.markdown("<h3 class='form-title'>Login</h3>", unsafe_allow_html=True)
email = st.text_input("Email", placeholder="you@email.com")
password = st.text_input("Password", type="password", placeholder="••••••••")

if st.button("Sign in", use_container_width=True):
    if not email or not password:
        st.warning("Semua field wajib diisi!")
    else:
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            role = user.get("role", "user")
            if role == "admin":
                st.success("Login Admin berhasil")
                st.switch_page("pages/10_admin_dashboard.py")
            else:
                st.warning("Login User berhasil")
                st.switch_page("pages/3_dashboard.py")
        else:
            st.error("Email atau password salah!")


st.markdown("<div class='divider'>or</div>", unsafe_allow_html=True)

st.markdown("<div class='switch-center'>Don't have an account?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1.8,3])

with col2:
    if st.button("Sign up", key="to_reg"):
        st.switch_page("pages/2_register.py")
        st.rerun()

 
st.markdown('</div>', unsafe_allow_html=True)