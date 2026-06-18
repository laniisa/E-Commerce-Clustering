import streamlit as st

def check_login():
    if "user" not in st.session_state:
        st.warning("Silakan login terlebih dahulu!")
        st.switch_page("pages/1_login.py")

def check_role(role_needed):

    check_login()

    user_role = st.session_state.user.get("role")

    if user_role != role_needed:
        st.error("Anda tidak memiliki akses ke halaman ini.")
        st.stop()
        
def check_admin():
    check_login()
    if (
        st.session_state.user.get("role")
        != "admin"
    ):
        st.error(
            "Halaman ini hanya untuk admin."
        )
        st.stop()

def load_css(*css_files):
    for css in css_files:
        with open(css, encoding="utf-8") as f: 
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_icons():
    st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css');
    </style>
    """, unsafe_allow_html=True)