import streamlit as st
from modules.auth_check import load_css

load_css("assets/style/sidebar.css")

def menu_item(label, page, icon, active, key):
    if active:
        st.markdown(f"""
        <div class="menu-item active">
            <span>{icon}</span> {label}
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button(f"{icon} {label}", key=key, use_container_width=True):
            st.switch_page(page)

def show_sidebar(active_page="dashboard"):
    with st.sidebar:

        st.markdown('<div class="sidebar">', unsafe_allow_html=True)

        # ======================
        # BRAND
        # ======================
        st.markdown("""
        <div class="brand">
            📊
            <div>
                <div class="brand-title">Clusterlytics</div>
                <div class="brand-sub">Data Clustering Tool</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ======================
        # MAIN MENU
        # ======================
        st.markdown('<div class="section-title">MAIN</div>', unsafe_allow_html=True)

        menu_item("Dashboard", "pages/3_dashboard.py", "🏠", active_page=="dashboard", "m1")
        menu_item("History", "pages/8_history.py", "🕒", active_page=="history", "m2")

        st.divider()

        # ======================
        # FLOW
        # ======================
        st.markdown('<div class="section-title">ANALYSIS FLOW</div>', unsafe_allow_html=True)

        def flow_item(label, page, icon, key):
            if st.button(f"{icon} {label}", key=key, use_container_width=True):
                st.switch_page(page)

        flow_item("Upload Data", "pages/4_upload_data.py", "①", "f1")
        flow_item("Preprocessing", "pages/5_preprocessing.py", "②", "f2")
        flow_item("EDA", "pages/6_eda.py", "③", "f3")
        flow_item("Clustering", "pages/7_clustering.py", "④", "f4")

        st.divider()

        # ======================
        # USER
        # ======================
        if "user" in st.session_state:
            st.markdown(f"""
            <div class="user-box">
                👤 {st.session_state.user['username']}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("pages/1_Login.py")

        st.markdown('</div>', unsafe_allow_html=True)