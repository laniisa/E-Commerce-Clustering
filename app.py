import streamlit as st

st.set_page_config(page_title="Clustering App", layout="wide")

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #f9fafb;
}
</style>
""", unsafe_allow_html=True)

st.title("Clustering App")

# cek login
st.switch_page("pages/1_login.py")