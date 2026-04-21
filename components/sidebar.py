import streamlit as st
from modules.auth_check import load_css

load_css("assets/style/sidebar.css")

def menu_item(label, page, active):
    if active:
        st.markdown(f'''
            <div class="sb-link active">{label}</div>
        ''', unsafe_allow_html=True)
    else:
        if st.button(label, key=label, use_container_width=True):
            st.switch_page(page)

def show_sidebar(active_page="dashboard"):
    with st.sidebar:

        st.markdown('<div class="sb-wrapper">', unsafe_allow_html=True)
    
        st.image("assets/image/clustering_icon.jpg", width=80)

        st.markdown("""
            <div class="sb-title">Clustering App</div>
            <div class="sb-sub">K-Medoids Analysis</div>
        """, unsafe_allow_html=True)

        
        # MAIN
        st.markdown('<div class="sb-group">MAIN</div>', unsafe_allow_html=True)
        
        menu_item("Dashboard", "pages/3_dashboard.py", active_page=="dashboard")
        menu_item("Panduan", "pages/9_guide.py", active_page=="guide")

        # CLUSTERING
        st.markdown('<div class="sb-group" >CLUSTERING</div>', unsafe_allow_html=True)
        
        menu_item("Upload Data", "pages/4_upload_data.py", active_page=="upload")
        menu_item("Preprocessing", "pages/5_preprocessing.py", active_page=="preprocessing")
        menu_item("EDA", "pages/6_eda.py", active_page=="eda",)
        menu_item("Clustering", "pages/7_clustering.py", active_page=="clustering")
        
        st.divider()
        # USER
        if "user" in st.session_state:
            st.markdown(f"""
            <div class="sb-user">
                👤 {st.session_state.user['username']}
            </div>
            """, unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("pages/1_Login.py")

        st.markdown('</div>', unsafe_allow_html=True)