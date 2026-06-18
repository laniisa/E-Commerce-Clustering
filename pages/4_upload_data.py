import streamlit as st
import pandas as pd
from modules.auth_check import *
from components.sidebar import show_sidebar
from modules.upload import *

load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/upload.css",
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("upload")

st.title("Upload Dataset")

st.markdown("""
<div class="alert-box">
Silakan unggah dataset penjualan multi-platform untuk memulai proses analisis clustering data menggunakan algoritma K-Medoids.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1.5], gap="large")

# UPLOAD (KIRI)
with col1:
    with st.container():
        st.markdown("### Form Upload Dataset")
        dataset_name = st.text_input("Nama Dataset")
        uploaded_files = st.file_uploader(
            "Upload file CSV / XLSX (nama file wajib mengandung platform: shopee/lazada/tiktok)",
            type=["csv", "xlsx"],
            accept_multiple_files=True)
        # VALIDASI FILE
        valid_files = []
        error_files = []
        if uploaded_files:
            for f in uploaded_files:
                name = f.name.lower()
                # validasi size 
                if f.size > 10 * 1024 * 1024:
                    error_files.append(f"{f.name} (terlalu besar)")
                    continue
                # validasi platform
                if not any(p in name for p in ["shopee", "lazada", "tiktok"]):
                    error_files.append(f"{f.name} (platform tidak dikenali)")
                    continue
                valid_files.append(f)
        if error_files:
            st.error("File tidak valid:")
            for e in error_files:
                st.write("-", e)
        if st.button("Upload Dataset", use_container_width=True):
            if not dataset_name:
                st.warning("Isi nama dataset dulu!")
            elif not valid_files:
                st.warning("Tidak ada file valid!")
            else:
                success, result = save_dataset(
                    st.session_state.user["id_user"],
                    dataset_name,
                    valid_files
                )
                if success:
                    st.success("Upload berhasil!")
                    st.session_state.active_dataset_id = result
                    st.rerun()
                else:
                    st.error(result)

# RIWAYAT (KANAN)

with col2:
    with st.container():
        st.markdown("### Riwayat Dataset")
        datasets = get_datasets(st.session_state.user["id_user"])

        search = st.text_input("", placeholder="🔍 Cari dataset...")
        if search:
            datasets = [d for d in datasets if search.lower() in d["dataset_name"].lower()]

        if len(datasets) == 0:
            st.warning("Belum ada dataset!")

        if "page" not in st.session_state:
            st.session_state.page = 1

        per_page = 4
        total = len(datasets)
        total_page = (total // per_page) + (1 if total % per_page else 0)

        start = (st.session_state.page - 1) * per_page
        current_data = datasets[start:start + per_page]

        st.markdown("""
        <div class="table-header">
            <div>Dataset</div>
            <div>File</div>
            <div>Aksi</div>
        </div>
        """, unsafe_allow_html=True)

        active_id = st.session_state.get("active_dataset_id")

        for d in current_data:
            class_name = "dataset-card active" if d["id"] == active_id else "dataset-card"
            is_active = "active-row" if d["id"] == active_id else ""

            c1, c2, c3 = st.columns([4,2,3])

            with c1:
                st.markdown(f'<div class="table-row {is_active}">{d["dataset_name"]}</div>', unsafe_allow_html=True)

            with c2:
                st.markdown(f'<div class="table-row center {is_active}">{d["total_files"]}</div>', unsafe_allow_html=True)

            with c3:
                d1,d2= st.columns(2)
                with d1:
                    if st.button(":material/visibility:", key=f"use_{d['id']}"):
                        st.session_state.active_dataset_id = d["id"]
                        st.rerun()
                with d2:
                    if st.button("🗑",key=f"delete_{d['id']}"):
                        delete_upload(d)
        
            # pagination
        p1, p2, p3 = st.columns([5,1,1])

        with p1:
            st.markdown(f'<div class="page-text">Page {st.session_state.page} of {total_page}</div>', unsafe_allow_html=True)

        with p2:
            if st.button("‹", key="prev_up"):
                if st.session_state.page > 1:
                    st.session_state.page -= 1
                    st.rerun()

        with p3:
            if st.button("›", key="next_up"):
                if st.session_state.page < total_page:
                    st.session_state.page += 1
                    st.rerun()
st.divider()

# PREVIEW DATA
if "active_dataset_id" in st.session_state:
    dataset = get_dataset_by_id(st.session_state.active_dataset_id)

    st.markdown(f"### Preview Dataset: {dataset['dataset_name']}")

    files = get_dataset_files(st.session_state.active_dataset_id)

    for file in files:
        df = pd.read_csv(file["file_path"])

        st.markdown(f"""
        <div class="summary-box">
            <div><b>{file['file_name']}</b></div>
            <div class="summary-meta">
                Platform: <span class="color">{file['platform']}</span> |
                Rows: {df.shape[0]} |
                Columns: {df.shape[1]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True, height=400)

    c1, c2 = st.columns([6,1])
        
    with  c2:
        if st.button(":material/arrow_forward: Lanjut", use_container_width=True):
            st.switch_page("pages/5_preprocessing.py")
else:
    st.info("Belum ada dataset aktif yang dipilih, silakan upload atau pilih dataset terlebih dahulu")