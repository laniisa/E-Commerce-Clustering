import streamlit as st
from modules.auth_check import load_css

def load_global_style():
    load_css("assets/style/style.css")


def show_header(title="Dashboard"):
    st.markdown("""
    <div class="custom-header">
        <div class="header-left">📊 Clustering App</div>
        <div class="header-right">K-Medoids Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"## {title}")


def show_footer():
    st.markdown("""
    <div class="footer">
        © 2026 K-Medoids App | Developed by Kamu
    </div>
    """, unsafe_allow_html=True)