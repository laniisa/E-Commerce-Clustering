import streamlit as st
import pandas as pd
from modules.auth_check import check_login
from components.sidebar import show_sidebar
from components.header import *
from modules.daashboard import get_clustering_history

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("history")