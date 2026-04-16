import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

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
            color="platform"
        )
        st.plotly_chart(fig2, use_container_width=True, height=200,)
    
    with tab2:
        fig1 = px.bar(
            platform_contribution,
            x="platform",
            y="total_sales",
            color="platform"
        )
        st.plotly_chart(fig1, use_container_width=True, height=200,)

    with tab3:
        st.dataframe(platform_contribution)
    
st.divider()

# ======================
# CORRELATION
# ======================
st.subheader("🔥 Korelasi")

col1, col2, col3 = st.columns([0.5, 2, 0.5])

with col2:
    fig, ax = plt.subplots(figsize=(4,3))
    sns.heatmap(
        correlation_matrix(df, num_cols),
        annot=True,
        cmap="coolwarm",
        ax=ax
    )
    st.pyplot(fig)

st.divider()

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
# TREND ANALYSIS
# ======================
st.subheader("📈 Analisis Tren Penjualan")

tab1, tab2, tab3= st.tabs([" Platform", "📊 Total Sales", "📄 Data"])

trend_all = monthly_trend(df)
trend_p = trend_platform(df)

with tab1:
    st.markdown("### 🔹 Tren Penjualan per Platform")

    fig = px.line(
        trend_p,
        x="year_month",
        y="total_sales",
        color="platform",
        markers=True,
        title="Trend per Platform"
    )

    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    # 🔹 TOTAL SALES TREND
    with col1:
        st.markdown("### 🔹 Total Sales Bulanan")

        fig = px.line(
            trend_all,
            x="year_month",
            y="total_sales",
            markers=True,
            title="Trend Total Penjualan"
        )

        fig.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Total Sales",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 QUANTITY TREND
    with col2:
        st.markdown("### 🔹 Total Produk Bulanan")

        fig = px.line(
            trend_all,
            x="year_month",
            y="quantity",
            markers=True,
            title="Trend Quantity"
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 PER PLATFORM
    

with tab3:
    st.markdown("### 📄 Data Trend")
    st.dataframe(trend_all)

st.divider()


# ======================
# CATEGORY ANALYSIS
# ======================
st.subheader("🛍️ Analisis Kategori Produk")

tab1, tab2, tab3= st.tabs(["📊 Per Platform", "📦 Total Sales & Quantity", "Data"])

with tab1:
    data_cp = category_platform(df)

    fig = px.bar(
        data_cp,
        x="product_category",
        y="total_sales",
        color="platform",
        barmode="group",
        title="Penjualan Kategori per Platform"
    )

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        data_cat = category_sales(df).reset_index()

        fig = px.bar(
            data_cat,
            x="product_category",
            y="total_sales",
            title="Total Penjualan per Kategori",
            color="product_category"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
# 🔹 QUANTITY PER CATEGORY
        data_qty = top_products(df).reset_index()

        fig = px.bar(
            data_qty,
            x="product_category",
            y="quantity",
            title="Jumlah Produk Terjual per Kategori",
            color="product_category"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(data_cp)

st.divider()

# ======================
# DISCOUNT EFFECT
# ======================
col1, col2 = st.columns(2)
with col1:
    st.subheader("📅 Pola Penjualan Harian")

    day_sales = sales_per_day(df).reset_index()

    fig = px.bar(
        day_sales,
        x="day_name",
        y="total_sales",
        title="Penjualan Berdasarkan Hari"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
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