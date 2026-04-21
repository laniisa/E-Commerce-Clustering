import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Riwayat Clustering", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.title {
    font-size: 28px;
    font-weight: 700;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

.stat {
    font-size: 22px;
    font-weight: 700;
}

.label {
    font-size: 13px;
    color: #6b7280;
}

/* TABLE STYLE */
thead tr th {
    background-color: #f9fafb !important;
    font-weight: 600 !important;
}

/* BUTTON */
.stButton>button {
    border-radius: 10px;
    font-weight: 600;
}

/* FILTER BOX */
.filter-box {
    background: white;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ================= DUMMY DATA =================
data = [
    {"id": 1, "tanggal": "2024-03-01", "jumlah_data": 18909, "cluster": 3, "metode": "K-Medoids", "dbi": 0.42},
    {"id": 2, "tanggal": "2024-03-05", "jumlah_data": 20000, "cluster": 4, "metode": "K-Medoids", "dbi": 0.38},
    {"id": 3, "tanggal": "2024-03-10", "jumlah_data": 15000, "cluster": 2, "metode": "K-Medoids", "dbi": 0.50},
]

df = pd.DataFrame(data)

# ================= HEADER =================
st.markdown('<div class="title">📊 Riwayat Clustering</div>', unsafe_allow_html=True)
st.write("Kelola dan lihat hasil clustering yang telah dilakukan")

st.markdown("")

# ================= STATS =================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><div class="label">Total Clustering</div><div class="stat">{}</div></div>'.format(len(df)), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="label">Rata-rata DBI</div><div class="stat">{:.2f}</div></div>'.format(df["dbi"].mean()), unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><div class="label">Cluster Terakhir</div><div class="stat">{}</div></div>'.format(df.iloc[-1]["cluster"]), unsafe_allow_html=True)

st.markdown("")

# ================= FILTER =================
st.markdown('<div class="filter-box">', unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)

with col_f1:
    cluster_filter = st.selectbox("Filter Cluster", ["Semua"] + sorted(df["cluster"].unique().tolist()))

with col_f2:
    date_filter = st.date_input("Filter Tanggal", value=None)

st.markdown('</div>', unsafe_allow_html=True)

# ================= APPLY FILTER =================
filtered_df = df.copy()

if cluster_filter != "Semua":
    filtered_df = filtered_df[filtered_df["cluster"] == cluster_filter]

if date_filter:
    filtered_df = filtered_df[filtered_df["tanggal"] == str(date_filter)]

st.markdown("")

# ================= TABLE =================
st.markdown("### 📋 Data Riwayat")

for i, row in filtered_df.iterrows():
    with st.container():
        col_a, col_b, col_c, col_d = st.columns([2,2,2,1])

        with col_a:
            st.markdown(f"""
            <div class="card">
            <div class="label">Tanggal</div>
            <div class="stat">{row['tanggal']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="card">
            <div class="label">Cluster</div>
            <div class="stat">{row['cluster']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c:
            st.markdown(f"""
            <div class="card">
            <div class="label">DBI</div>
            <div class="stat">{row['dbi']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_d:
            if st.button("Detail", key=f"detail_{row['id']}"):
                st.session_state.selected = row.to_dict()
                st.switch_page("pages/detail_riwayat.py")

            if st.button("Hapus", key=f"delete_{row['id']}"):
                st.warning(f"Data ID {row['id']} dihapus (dummy)")

    st.markdown("")

# ================= EMPTY STATE =================
if filtered_df.empty:
    st.info("Tidak ada data ditemukan")