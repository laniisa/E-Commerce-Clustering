import streamlit as st
import pandas as pd
from modules.auth_check import check_login, load_css
from components.sidebar import show_sidebar
from modules.upload import get_dataset_files
from modules.preprocessing import *

# ======================
# CONFIG
# ======================
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

load_css(
    "assets/style/style.css",
    "assets/style/preprocessing.css"
)

check_login()
show_sidebar("preprocessing")

# ======================
# LOAD DATASET
# ======================
dataset_id = st.session_state.get("active_dataset_id")
st.title("⚙️ Preprocessing Data")

if not dataset_id:
    st.warning("Pilih dataset dulu di halaman upload!")
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

# ======================
# INIT SESSION STATE
# ======================
if "pipeline" not in st.session_state:
    st.session_state.pipeline = {
        "cleaning": False,
        "selection": False,
        "transform": False,
        "integration": False,
        "normalization": False
    }

# reset kalau dataset beda
if "last_dataset_id" not in st.session_state:
    st.session_state.last_dataset_id = dataset_id

if st.session_state.last_dataset_id != dataset_id:
    st.session_state.pipeline = {
        "cleaning": False,
        "selection": False,
        "transform": False,
        "integration": False,
        "normalization": False
    }

    for key in ["cleaned", "selected", "transformed", "integrated", "normalized"]:
        st.session_state.pop(key, None)

    st.session_state.last_dataset_id = dataset_id

# ======================
# HEADER
# ======================
st.caption("Pipeline pembersihan & transformasi data multi-platform")


st.markdown("### 🔄 Progress Pipeline")
if "active_step" not in st.session_state:
    st.session_state.active_step = "preview"
steps = [
    ("preview", "Preview"),
    ("cleaning", "Cleaning"),
    ("selection", "Selection"),
    ("transform", "Transform"),
    ("integration", "Integration"),
    ("normalization", "Normalization")
]

cols = st.columns(len(steps))

cols = st.columns(len(steps))

for i, (key, label) in enumerate(steps):

    is_done = st.session_state.pipeline.get(key, False)
    is_active = st.session_state.active_step == key

    icon = "✅" if is_done else "⬜"
    if cols[i].button(f"{icon}\n{label}", key=f"step_{key}"):
        st.session_state.active_step = key


# ======================
# PREVIEW (RINGKASAN, BUKAN TABLE)
# ======================
if st.session_state.active_step == "preview":

    st.markdown("### 📊 Ringkasan Dataset")

    total_rows, total_cols, total_missing = dataset_overview(raw_dfs)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Data", total_rows)
    c2.metric("Total Kolom", total_cols)
    c3.metric("Total Missing", total_missing)
    c4.metric("Jumlah File", len(raw_dfs))

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


# ======================
# CLEANING
# ======================
elif st.session_state.active_step == "cleaning":

    if "cleaned" not in st.session_state:
        st.session_state.cleaned = [
            clean_data(df, p)
            for df, p in zip(raw_dfs, platforms)
        ]
        st.session_state.pipeline["cleaning"] = True

    st.markdown("### 🧹 Hasil Cleaning")

    total_rows, total_cols, total_missing = dataset_overview(st.session_state.cleaned)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", total_rows)
    c2.metric("Columns", total_cols)
    c3.metric("Missing", total_missing)

    show_quality(pd.concat(st.session_state.cleaned))

    for df, file in zip(st.session_state.cleaned, files):
        show_summary(df, file["file_name"], file["platform"])
        st.dataframe(df, use_container_width=True, height=400)
# ======================
# SELECTION
# ======================
elif st.session_state.active_step == "selection":

    if not st.session_state.pipeline["cleaning"]:
        st.warning("⚠️ Cleaning dulu!")
        st.stop()

    if "selected" not in st.session_state:
        st.session_state.selected = [
            select_columns(df, p)
            for df, p in zip(st.session_state.cleaned, platforms)
        ]
        st.session_state.pipeline["selection"] = True

    st.markdown("### 🎯 Hasil Selection")

    show_quality(pd.concat(st.session_state.selected))

    for df, file in zip(st.session_state.selected, files):
        show_summary(df, file["file_name"], file["platform"])
        st.dataframe(df, use_container_width=True, height=400)

# ======================
# TRANSFORM
# ======================
elif st.session_state.active_step == "transform":

    if not st.session_state.pipeline["selection"]:
        st.warning("⚠️ Selection dulu!")
        st.stop()

    if "transformed" not in st.session_state:
        st.session_state.transformed = [
            transform_data(df, p)
            for df, p in zip(st.session_state.selected, platforms)
        ]
        st.session_state.pipeline["transform"] = True

    st.markdown("### 🔄 Hasil Transform")

    total_rows, total_cols, total_missing = dataset_overview(st.session_state.transformed)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", total_rows)
    c2.metric("Columns", total_cols)
    c3.metric("Missing", total_missing)

    show_quality(pd.concat(st.session_state.transformed))
    
    for df, file in zip(st.session_state.transformed, files):
        show_summary(df, file["file_name"], file["platform"])
        st.dataframe(df, use_container_width=True, height=400)
    
# ======================
# INTEGRATION
# ======================
elif st.session_state.active_step == "integration":

    if not st.session_state.pipeline["transform"]:
        st.warning("⚠️ Transform dulu!")
        st.stop()

    if "integrated" not in st.session_state:
        st.session_state.integrated = integrate_data(
            st.session_state.transformed
        )
        st.session_state.pipeline["integration"] = True

    st.markdown("### 🔗 Hasil Integration")

    df = st.session_state.integrated

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", df.isna().sum().sum())

    show_quality(df)

    st.dataframe(st.session_state.integrated, use_container_width=True, height=500)
# ======================
# NORMALIZATION
# ======================
elif st.session_state.active_step == "normalization":

    if not st.session_state.pipeline["integration"]:
        st.warning("⚠️ Integration dulu!")
        st.stop()

    if "normalized" not in st.session_state:
        st.session_state.normalized = normalize_data(
            st.session_state.integrated
        )
        st.session_state.pipeline["normalization"] = True

    df = st.session_state.normalized

    st.markdown("### 📊 Data Final (Siap Clustering)")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", df.isna().sum().sum())

    show_quality(df)
    
    st.dataframe(st.session_state.normalized, use_container_width=True, height=500)

    st.success("Data siap untuk clustering ")
# ======================
# NAV BUTTON
# ======================
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.switch_page("pages/4_upload_data.py")

    with col3:
        if st.button("➡️ Lanjut", use_container_width=True):
            st.switch_page("pages/6_eda.py")