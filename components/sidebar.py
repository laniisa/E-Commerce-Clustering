import streamlit as st
from modules.auth_check import *

load_icons()
load_css("assets/style/sidebar.css", "assets/style/style.css")


def show_sidebar(active_page="dashboard"):
    role = st.session_state.user.get( "role", "user")

    with st.sidebar:

        st.image("assets/image/clustering_icon.jpg", width=75)
        
        st.markdown("""
            <div class="sb-title">Clustering App</div>
            <div class="sb-sub">K-Medoids Analysis</div>
        """, unsafe_allow_html=True)

        if role == "admin":

            menu = {
                "ADMIN": [
                    ("Dashboard Admin", "pages/10_admin_dashboard.py",
                     ":material/dashboard:", "dashboard_admin"),
                ],

            }

        else:
            menu = {
                "MAIN": [
                    ("Dashboard", "pages/3_dashboard.py", ":material/home:", "dashboard"),
                    ("Panduan", "pages/9_panduan.py", ":material/menu_book:", "panduan"),
                ],
                "CLUSTERING": [
                    ("Upload Data", "pages/4_upload_data.py", ":material/upload:", "upload"),
                    ("Preprocessing", "pages/5_preprocessing.py", ":material/settings:", "preprocessing"),
                    ("EDA", "pages/6_eda.py", ":material/bar_chart:", "eda"),
                    ("Clustering", "pages/7_clustering.py", ":material/account_tree:", "clustering"),
                ]
            }

        
        for group, items in menu.items():
            st.markdown(f'<div class="sb-group">{group}</div>', unsafe_allow_html=True)
            
            for label, page, icon, key in items:
                st.page_link(page, label=label, icon=icon)

        # BOTTOM 
        st.markdown('<div class="sb-bottom">', unsafe_allow_html=True)

        if "user" in st.session_state:
            st.markdown(f'<div class="sb-user">👤 {st.session_state.user["username"]} <br> {role.title()} </div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([0.4, 2.2, 0.4])
        with col2:
            if st.button("⎋ Logout", key="logout_btn", use_container_width=True):
                st.session_state.clear()
                st.switch_page("app.py")
        st.markdown("</div>", unsafe_allow_html=True)