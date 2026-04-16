import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

from modules.auth_check import check_login, load_css
from components.sidebar import show_sidebar
from modules.eda import *


st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

load_css(
    "assets/style/style.css",
    "assets/style/eda.css"
)
check_login()
show_sidebar("eda")

# ======================
# LOAD DATA (IMPORTANT 🔥)
# ======================
st.title("📊 Exploratory Data Analysis")


if "integrated" not in st.session_state:
    st.warning("Silahkan lakukan preprocessing terlebih dahulu!")
    st.stop()

df = st.session_state.integrated.copy()
df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

num_cols = ["price", "discount", "quantity", "total_sales"]

col1, col2 = st.columns(2)

with col1:
    selected_platform = st.multiselect(
        "Pilih Platform",
        options=df["platform"].unique(),
        default=df["platform"].unique()
    )

with col2:
    date_range = st.date_input(
        "Filter Tanggal",
        [df["transaction_date"].min(), df["transaction_date"].max()]
    )

df = df[
    (df["platform"].isin(selected_platform)) &
    (df["transaction_date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]
# ======================
# OVERVIEW
# ======================
info = get_overview(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data", info["total_data"])
col2.metric("Kategori", info["total_category"])
col3.metric("Platform", info["total_platform"])
col4.metric("Periode", f"{info['min_date'].date()}")

st.divider()

# ======================
# DESCRIPTIVE
# ======================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Statistik Deskriptif")
    st.dataframe(
        descriptive_stats(df, num_cols),
        use_container_width=True,
        height=350,
    )

with col2:
    st.subheader("🛒 Platform Performance")

    platform_contribution = (
        df.groupby("platform")
        .agg(
            total_sales=("total_sales", "sum"),
            total_transaksi=("product_code", "count")
        )
        .reset_index()
    )

    tab1, tab2, tab3 = st.tabs(["📊 Transaksi", "📊 Total Sales", "📄 Data"])
    
    with tab1:
        fig2 = px.bar(
            platform_contribution,
            x="platform",
            y="total_transaksi",
            color="platform",
            title="Total Transaksi"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        fig1 = px.bar(
            platform_contribution,
            x="platform",
            y="total_sales",
            color="platform",
            title="Total Sales per Platform"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with tab3:
        st.dataframe(platform_contribution)
    
st.divider()

# ======================
# CORRELATION
# ======================
st.subheader("🔥 Korelasi")

fig, ax = plt.subplots(figsize=(6,4))
sns.heatmap(correlation_matrix(df, num_cols), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# PER PLATFORM
st.subheader("📊 Korelasi per Platform")
corrs = corr_per_platform(df, num_cols)

cols = st.columns(len(corrs))
for i, (p, corr) in enumerate(corrs.items()):
    with cols[i]:
        fig, ax = plt.subplots(figsize=(4,3))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.caption(p)
        st.pyplot(fig)

st.divider()

# ======================
# DISTRIBUTION
# ======================
st.subheader("📊 Distribusi Data")

col_dis = st.selectbox("Pilih Kolom", num_cols, key="dist")

tab1, tab2 = st.tabs(["📊 Visual", "📄 Data"])

with tab1:
    col1, col2 = st.columns(2)

    # 🔹 OVERALL
    with col1:
        st.markdown("### 🔹 Distribusi Keseluruhan")

        fig = px.histogram(
            df,
            x=col_dis,
            marginal="box",
            title=f"Distribusi {col_dis}",
        )

        fig.update_layout(
            template="plotly_white",
            bargap=0.1
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 PER PLATFORM
    with col2:
        st.markdown("### 🔹 Distribusi per Platform")

        fig = px.histogram(
            df,
            x=col_dis,
            color="platform",
            marginal="box"
        )

        fig.update_layout(template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df[[col_dis, "platform"]])

st.divider()


# ======================
# BOXPLOT (PLOTLY)
# ======================
st.subheader("📦 Boxplot")

col_box = st.selectbox("Pilih Kolom", num_cols, key="box")

tab1, tab2 = st.tabs(["📊 Visual", "📄 Data"])

with tab1:
    col1, col2 = st.columns(2)

    # 🔹 OVERALL
    with col1:
        st.markdown("### 🔹 Boxplot Keseluruhan")

        fig = px.box(
            df,
            y=col_box,
            points="outliers",
            title=f"Boxplot {col_box}"
        )

        fig.update_layout(template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 PER PLATFORM
    with col2:
        st.markdown("### 🔹 Boxplot per Platform")

        fig = px.box(
            df,
            x="platform",
            y=col_box,
            color="platform",
            points="outliers"
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_tickangle=-30
        )

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df[[col_box, "platform"]])

st.divider()

# ======================
# TREND
# ======================
st.subheader("📈 Trend Bulanan")
tab1, tab2 = st.tabs(["📊 Visual", "📄 Data"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        trend = monthly_trend(df)

        fig = px.line(
            trend,
            x="platform",
            y="total_sales",
            markers=True,
            title="Trend Penjualan"
        )

    with col2:
        trend_p = trend_platform(df)

        fig = px.line(
            trend,
            x="year_month",
            y="total_sales",
            markers=True,
            title="Trend Penjualan"
        )

        st.plotly_chart(fig, use_container_width=True)
with tab2:
    st.dataframe(trend)

st.divider()

# ======================
# CATEGORY
# ======================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Kategori")
    st.bar_chart(category_sales(df))

with col2:
    st.markdown("### Top Produk")
    st.bar_chart(top_products(df))

st.divider()

# ======================
# DISCOUNT EFFECT
# ======================
st.subheader("💸 Discount vs Sales")

df_scatter = df.dropna(subset=["discount", "total_sales"])
if not df_scatter.empty:
    fig = px.scatter(
        df_scatter,
        x="discount",
        y="total_sales",
        color="platform"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data kosong")

st.divider()


col1, col2, col3 = st.columns([1, 6 ,1])

with col1:
    if st.button("⬅️ Kembali", use_container_width=True):
        st.switch_page("pages/5_preprocessing.py")

with col3:
    if st.button("➡️ Lanjut", use_container_width=True):
        st.switch_page("pages/7_clustering.py")