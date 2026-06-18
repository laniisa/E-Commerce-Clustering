import streamlit as st
import pandas as pd
from modules.auth_check import *
from components.sidebar import show_sidebar
from modules.upload import get_dataset_files
from modules.preprocessing import *

load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/preprocessing.css"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("preprocessing")


dataset_id = st.session_state.get("active_dataset_id")

st.title("Preprocessing Data")
st.markdown(f"""
<div class="alert-box">
    <div class="alert-desc">
        Halaman ini menampilkan proses preprocessing data yang dilakukan untuk mempersiapkan dataset sebelum analisis clustering.
    </div>
</div>
""", unsafe_allow_html=True)
if not dataset_id:
    st.warning("Silahkan pilih dataset terlebih dahulu di halaman upload!")
    st.stop()

files = get_dataset_files(dataset_id)

raw_dfs = []
platforms = []

for file in files:
    if file["file_name"].endswith(".csv"):
        df = pd.read_csv(file["file_path"])
    else:
        df = pd.read_excel(file["file_path"])

    raw_dfs.append(df)
    platforms.append(file["platform"])


if "pipeline" not in st.session_state:
    st.session_state.pipeline = {
        "preview": True,
        "cleaning": False,
        "selection": False,
        "transform": False,
        "integration": False
    }

# reset kalau dataset beda
if "last_dataset_id" not in st.session_state:
    st.session_state.last_dataset_id = dataset_id

if st.session_state.last_dataset_id != dataset_id:
    st.session_state.pipeline = {
        "preview": True,
        "cleaning": False,
        "selection": False,
        "transform": False,
        "integration": False
    }

    for key in ["cleaned", "selected", "transformed", "integrated", "normalized"]:
        st.session_state.pop(key, None)

    st.session_state.last_dataset_id = dataset_id


st.caption("Pipeline pembersihan & transformasi data multi-platform")


st.markdown("### Progress Pipeline")
if "active_step" not in st.session_state:
    st.session_state.active_step = "preview"
steps = [
    ("preview", "Preview"),
    ("cleaning", "Cleaning"),
    ("selection", "Selection"),
    ("transform", "Transform"),
    ("integration", "Integration")
]

cols = st.columns(len(steps))

for i, (key, label) in enumerate(steps):

    is_done = st.session_state.pipeline.get(key, False)
    is_active = st.session_state.active_step == key

    icon = "✅" if is_done else "⬜"
    if cols[i].button(f"{icon}\n{label}", key=f"step_{key}"):
        st.session_state.active_step = key
        if key == "cleaning":
            st.session_state.pipeline["cleaning"] = True

        elif key == "selection":
            if st.session_state.pipeline["cleaning"]:
                st.session_state.pipeline["selection"] = True

        elif key == "transform":
            if st.session_state.pipeline["selection"]:
                st.session_state.pipeline["transform"] = True

        elif key == "integration":
            if st.session_state.pipeline["transform"]:
                st.session_state.pipeline["integration"] = True

        st.rerun()

st.divider()

# PREVIEW 

if st.session_state.active_step == "preview":

    st.markdown("### Ringkasan Dataset")

    total_rows, total_cols, total_missing = dataset_overview(raw_dfs)

    c1, c2, c3, c4 = st.columns(4)

    data_metric = [
        ("Total Data", total_rows),
        ("Total Kolom", total_cols),
        ("Total Missing", total_missing),
        ("Jumlah File", len(raw_dfs))
    ]

    for col, item in zip([c1,c2,c3,c4], data_metric):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{item[0]}</div>
                <div class="metric-value">{item[1]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    for df, file in zip(raw_dfs, files):

        st.markdown(f"""
        <div class="block">
            📄 <b>{file['file_name']}</b><br>
            Platform: {file['platform']}
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing", df.isna().sum().sum())

    st.info("Data siap untuk preprocessing")

    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.switch_page("pages/4_upload_data.py")



# CLEANING

elif st.session_state.active_step == "cleaning":

    if "cleaned" not in st.session_state:
        st.session_state.cleaned = [
            clean_data(df, p)
            for df, p in zip(raw_dfs, platforms)
        ]
        
    st.markdown("### Hasil Cleaning")

    before_rows, before_cols, before_missing = dataset_overview(raw_dfs)
    after_rows, after_cols, after_missing = dataset_overview(st.session_state.cleaned)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Rows", after_rows, after_rows-before_rows)
    c2.metric("Columns", after_cols, after_cols-before_cols)
    c3.metric("Missing", after_missing, after_missing-before_missing)

    st.success("""
        Sistem berhasil menghapus data transaksi batal, retur, refund, 
        serta data yang tidak memenuhi status transaksi selesai pada masing-masing platform.
        """)
    show_quality(pd.concat(st.session_state.cleaned))
    
    for df,file in zip(st.session_state.cleaned, files):
        st.markdown(f"""
        <div class="block">
        <b>{file['file_name']}</b><br>
        Platform: {file['platform']} | Rows: {df.shape[0]} | Columns: {df.shape[1]} | Missing: {df.isna().sum().sum()}
        </div>
        """, unsafe_allow_html=True)

        
        st.dataframe(df, use_container_width=True, height=300)


# SELECTION

elif st.session_state.active_step == "selection":

    if not st.session_state.pipeline["cleaning"]:
        st.warning("Lakukan Cleaning terlebih dahulu!")
        st.stop()

    if "selected" not in st.session_state:
        st.session_state.selected = [
            select_columns(df, p)
            for df, p in zip(st.session_state.cleaned, platforms)
        ]
        
    st.markdown("### Hasil Selection")
    st.success("Sistem menyeleksi hanya atribut yang relevan terhadap analisis penjualan dan clustering.")
    
    for df, file in zip(st.session_state.selected, files):
        st.markdown(f"""
        <div class="block">
        <b>{file['file_name']}</b><br>
        Platform: {file['platform']} | Rows: {df.shape[0]} | Columns: {df.shape[1]}
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True, height=300)


# TRANSFORM

elif st.session_state.active_step == "transform":

    if not st.session_state.pipeline["selection"]:
        st.warning("Lakukan Selection terlebih dahulu!")
        st.stop()

    if "transformed" not in st.session_state:
        st.session_state.transformed = [
            transform_data(df, platform)
            for df, platform in zip(st.session_state.selected, platforms)
        ]
    st.markdown("###  Hasil Transform")
    total_rows, total_cols, total_missing = dataset_overview(st.session_state.transformed)

    df_tf = pd.concat(st.session_state.transformed, ignore_index=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Rows", total_rows)
    c2.metric("Unique Prroduct", df_tf["product_name"].nunique())
    c3.metric("Platform", df_tf["platform"].nunique())
    
    st.success("""
    Sistem berhasil melakukan standardisasi struktur data multi-platform,
    pembersihan numerik, normalisasi nama produk, serta pembentukan dataset analisis untuk proses clustering.
    """)
    
    for df, file in zip(st.session_state.transformed, files):
        st.markdown(f"""
        <div class="block">
        <b>{file['file_name']}</b><br>
        Platform: {file['platform']} | Rows: {df.shape[0]} | Columns: {df.shape[1]}
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df, use_container_width=True, height=300)
    
    
# INTEGRATION

elif st.session_state.active_step == "integration":

    if not st.session_state.pipeline["transform"]:
        st.warning("Lakukan Transform terlebih dahulu!")
        st.stop()

    if "integrated" not in st.session_state:
        merged = integrate_data(st.session_state.transformed)
        st.session_state.integrated = merged

    df = st.session_state.integrated

    st.markdown("### Hasil Integration")

    c1,c2,c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", df.isna().sum().sum())

    st.success("Sistem berhasil mengintegrasikan seluruh data platform .")
    show_quality(df)
    st.dataframe(df, use_container_width=True, height=450)

# BUTTON

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.switch_page("pages/4_upload_data.py")

    with col3:
        if st.button("➡️ Lanjut", use_container_width=True):
            st.switch_page("pages/6_eda.py")