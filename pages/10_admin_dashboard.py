import streamlit as st

import plotly.express as px

from modules.auth_check import *
from modules.admin_dashboard import *
from components.sidebar import show_sidebar


load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/admin_dashboard.css",
)
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Admin Dashboard")

check_admin()
show_sidebar(dashboard_admin)

user_name = st.session_state.user["username"]
data = dashboard_admin()

st.title("Dashboard Admin")
st.markdown(f"""
<div class="alert-box">
    <div class="alert-title">Selamat Datang, {user_name} 👋</div>
    <div class="alert-desc">
        "Monitoring pengguna dan aktivitas analisis sistem"
    </div>
</div>
""", unsafe_allow_html=True)
m1,m2,m3= st.columns(3)
metric_data = [
    ("Total Dataset", data["total_dataset"]),
    ("Total File", data["total_files"]),
    ("Total Analisis", data["total_analisis"])
]

for col, item in zip([m1,m2,m3], metric_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{item[0]}</div>
            <div class="metric-value">{item[1]}</div>
        </div>
        """, unsafe_allow_html=True)


st.divider()

d1,d2 = st.columns([2,1])
with d1:
    tab1, tab2, tab3 = st.tabs(["📊 Riwayat Analisis", "👤 Pengguna", "🗂️ Dataset"])

    # MANAJEMEN USERS

    with tab1:
        st.subheader("Riwayat Analisis")

        history = get_history()

        search = st.text_input("", placeholder="🔍 Cari Analisis...")
        
        if search:
            history = history[
                history["dataset_name"].str.contains(search, case=False, na=False)
                |
                history["username"].str.contains(search, case=False, na=False)
            ]

        if history.empty:
            st.warning("Belum ada riwayat analisis!")

        else:
            per_page = 10
            total = len(history)
            total_page = (total - 1) // per_page + 1

            if "page_history" not in st.session_state:
                st.session_state.page_history = 1

            start = (st.session_state.page_history - 1) * per_page

            current_history = history.iloc[start:start + per_page]

            h1,h2,h3,h4,h5,h6,h7,h8,h9 = st.columns(
                [1,1,2,2,1,2,1,2,2]
            )

            h1.markdown("**No**")
            h2.markdown("**User**")
            h3.markdown("**Dataset**")
            h4.markdown("**Metode**")
            h5.markdown("**K**")
            h6.markdown("**Silhouette**")
            h7.markdown("**DBI**")
            h8.markdown("**Tanggal**")
            h9.markdown("**Aksi**")

            st.divider()
            for i, (_, row) in enumerate(
                current_history.iterrows(),start=start + 1 ):
                c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns([1,1,2,2,1,2,1,2,2])

                c1.write(i)
                c2.write(row["username"])
                c3.write(row["dataset_name"])
                c4.write(row["method"])
                c5.write(row["k_cluster"])
                c6.write( round(row["silhouette_score"],3))
                c7.write(round(row["dbi_score"],3))
                c8.write(row["created_at"].strftime("%d-%m-%Y"))
                with c9:
                    b1,b2 = st.columns(2)
                    with b1:
                        if st.button(":material/visibility:",
                            key=f"detail_{row['id']}"):
                            detail_analisis(row)

                    with b2:
                        if st.button(":material/delete:",
                            key=f"delete_{row['id']}"):
                            delete_analisis(row)
            st.divider()

            p1,p2,p3 = st.columns([12,1,1])

            with p1:
                st.caption(
                    f"Page {st.session_state.page_history} "f"of {total_page}")

            with p2:
                if st.button("‹", key="prev_history"):
                    if st.session_state.page_history > 1:
                        st.session_state.page_history -= 1
                        st.rerun()
            with p3:
                if st.button("›",key="next_history"):
                    if (st.session_state.page_history < total_page):
                        st.session_state.page_history += 1
                        st.rerun()

    # RIWAYAT ANALISIS
    with tab2:
        
        st.subheader("Manajemen Pengguna")
        if st.button(":material/person_add: Add User"):
            add_user()
        if st.session_state.get("user_added"):
            st.success("User berhasil ditambahkan")
            del st.session_state["user_added"]

        users = get_users()
        search_user = st.text_input(
            "",placeholder="🔍 Cari user...",key="search_user")
        if search_user:
            users = users[
                users["username"].str.contains(search_user, case=False,na=False)
            ]
        if users.empty:
            st.warning("Belum ada user!")
        else:
            per_page = 5
            total = len(users)
            total_page = (total - 1) // per_page + 1

            if "page_users" not in st.session_state:
                st.session_state.page_users = 1

            start = (st.session_state.page_users - 1) * per_page

            current_users = users.iloc[start:start + per_page]
            h1,h2,h3,h4,h5,h6 = st.columns([1,2,3,1,2,2])

            h1.markdown("**No**")
            h2.markdown("**User**")
            h3.markdown("**Email**")
            h4.markdown("**Role**")
            h5.markdown("**Tanggal**")
            h6.markdown("**Aksi**")

            st.divider()
            for d, (_, row) in enumerate(
                current_users.iterrows(),start=start + 1
            ):
                c1,c2,c3,c4,c5,c6 = st.columns([1,2,3,1,2,2])
                c1.write(d)
                c2.write(row["username"])
                c3.write(row["email"])
                c4.write(row["role"])
                c5.write(row["created_at"].strftime("%d-%m-%Y"))
                with c6:
                    b1,b2 = st.columns(2)
                    with b1:
                        if st.button( ":material/edit:",
                            key=f"user_edit_{row['id_user']}"
                        ):
                            edit_user(row)

                    with b2:
                        if st.button(":material/delete:",
                            key=f"user_delete_{row['id_user']}"
                        ):
                            confirm_delete(row)

            st.divider()
            p1,p2,p3 = st.columns([9,1,1])

            with p1:
                st.caption(
                    f"Page {st.session_state.page_users} "
                    f"of {total_page}"
                )

            with p2:
                if st.button("‹",key="prev_users"):
                    if st.session_state.page_users > 1:
                        st.session_state.page_users -= 1
                        st.rerun()

            with p3:
                if st.button("›",key="next_users"):
                    if (st.session_state.page_users < total_page):
                        st.session_state.page_users += 1
                        st.rerun()

    with tab3:

        st.subheader("Manajemen Dataset")
        datasets = get_datasets()
        search_ds = st.text_input("",placeholder="🔍 Cari dataset...",key="search_dataset")
        if search_ds:
            datasets = datasets[
                datasets["dataset_name"].str.contains(
                    search_ds,
                    case=False,
                    na=False
                )
            ]
        if datasets.empty:
            st.warning("Belum ada dataset!")
        else:
            per_page = 6
            total = len(datasets)
            total_page = (total - 1) // per_page + 1

            if "page_datasets" not in st.session_state:
                st.session_state.page_datasets = 1

            start = (st.session_state.page_datasets - 1) * per_page
            current_datasets = datasets.iloc[start:start + per_page]

            h1,h2,h3,h4,h5,h6 = st.columns(
                [1,2,2,2,2,2]
            )
            h1.markdown("**No**")
            h2.markdown("**User**")
            h3.markdown("**Dataset**")
            h4.markdown("**Total File**")
            h5.markdown("**Upload**")
            h6.markdown("**Aksi**")

            st.divider()
            for i, (_, row) in enumerate(current_datasets.iterrows(),start=start + 1):
                c1,c2,c3,c4,c5,c6 = st.columns([1,2,2,2,2,2])

                c1.write(i)
                c2.write(row["username"])
                c3.write(row["dataset_name"])
                c4.write(row["total_files"])
                c5.write(row["created_at"].strftime("%d-%m-%Y"))
                with c6:
                    b1,b2 = st.columns(2)
                    with b1:
                        if st.button(":material/visibility:",
                            key=f"dataset_detail_{row['id']}"
                        ):
                            detail_datasets(row)
                    with b2:
                        if st.button(":material/delete:",
                            key=f"dataset_delete_{row['id']}"
                        ):
                            delete_datasets(row)

            st.divider()

            p1,p2,p3 = st.columns([9,1,1])

            with p1:
                st.caption(
                    f"Page {st.session_state.page_datasets} "
                    f"of {total_page}"
                )

            with p2:
                if st.button("‹", key="prev_datasets"):
                    if st.session_state.page_datasets> 1:
                        st.session_state.page_datasets -= 1
                        st.rerun()

            with p3:
                if st.button("›",key="next_datasets"):
                    if (
                        st.session_state.page_datasets
                        < total_page
                    ):
                        st.session_state.page_datasets += 1
                        st.rerun()    
        
with d2:
    platform_data = get_platform_chart()
    
    st.subheader("Distribusi File per Platform")
    fig = px.pie(
        platform_data,
        names="platform",
        values="total",
        hole=0.55,
        title="Dataset per Platform"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        height=400,
        showlegend=True,
        margin=dict(t=50,b=10,l=10,r=10)
    )

    st.plotly_chart(fig, use_container_width=True)


    
