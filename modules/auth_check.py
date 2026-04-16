import streamlit as st

def check_login():
    if "user" not in st.session_state:
        st.warning("Silakan login terlebih dahulu!")
        st.switch_page("pages/1_login.py")

def load_css(*css_files):
    for css in css_files:
        with open(css, encoding="utf-8") as f: 
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
