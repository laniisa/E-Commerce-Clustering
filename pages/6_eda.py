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
    "assets/style/sidebar.css",
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
    st.subheader(" Statistik Deskriptif")
    st.dataframe(
        descriptive_stats(df, num_cols),
        use_container_width=True,
        height=350,
    )

with col2:
    st.subheader("Platform Performance")

    platform_data = platform_contribution(df)

    tab1, tab2, tab3 = st.tabs(["Transaksi", "Total Sales", "Data"])
    
    with tab1:
        fig2 = px.bar(
            platform_data,
            x="platform",
            y="total_transaksi",
            color="platform"
        )
        st.plotly_chart(fig2, use_container_width=True, height=200,)
    
    with tab2:
        fig1 = px.bar(
            platform_data,
            x="platform",
            y="total_sales",
            color="platform"
        )
        st.plotly_chart(fig1, use_container_width=True, height=200,)

    with tab3:
        st.dataframe(platform_data)
    
st.divider()

# ======================
# DISTRIBUTION
# ======================
st.subheader("Distribusi Data")

col_dis = st.selectbox("Pilih Kolom", num_cols, key="dist")

tab1, tab2 = st.tabs(["Visualisasi", "Data"])

with tab1:
    col1, col2 = st.columns(2)

    # 🔹 OVERALL
    with col1:

        fig = px.histogram(
            df,
            x=col_dis,
            marginal="box",
            title=f"Distribusi {col_dis} global",
        )

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Poppins", size=12),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 PER PLATFORM
    with col2:
        
        fig = px.histogram(
            df,
            x=col_dis,
            color="platform",
            marginal="box",
            title=f"Distribusi {col_dis} per platform",
        )

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Poppins", size=12),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df[[col_dis, "platform"]])

st.divider()

col1,col2, col3 = st.columns(3)
with col1:
    # ======================
    # SKEWNESS
    # ======================
    st.subheader("Skewness")

    skew_df = pd.DataFrame({
        "Feature": num_cols,
        "Skewness": [df[c].skew() for c in num_cols]
    })

    st.dataframe(skew_df)
with col2:
    # ======================
    # OUTLIER (IQR)
    # ======================
    st.subheader("Outlier (IQR)")

    outlier_data = []

    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]

        outlier_data.append({
            "Feature": col,
            "Jumlah Outlier": len(outliers),
            "Persentase (%)": round(len(outliers)/len(df)*100, 2)
        })

    df_outlier = pd.DataFrame(outlier_data)

    st.dataframe(df_outlier)

with col3:
    st.subheader("Penanganan Outlier")

    if st.button("Tangani Outlier (Log + RobustScaler)"):

        st.session_state.normalized = normalize_data(df)

        st.success("✅ Data berhasil dinormalisasi !")

st.divider()

if "normalized" in st.session_state:

    st.subheader("Distribusi Setelah Normalisasi")

    df_norm = st.session_state.normalized

    col = st.selectbox("Pilih Kolom (Normalized)", num_cols, key="norm")

    col1, col2= st.columns(2)
    with col1:

        fig = px.histogram(df_norm, x=col, marginal="box", title=f"Distribusi {col} global")
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Poppins", size=12),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(df_norm, x=col, color="platform", marginal="box", title=f"Distribusi {col} per platform",)

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Poppins", size=12),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)


st.divider()

# ======================
# CORRELATION
# ======================
st.subheader("Matriks Korelasi")

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
st.subheader("Korelasi per Platform")
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
# TREND ANALYSIS
# ======================
st.subheader("Analisis Tren Penjualan")

tab1, tab2, tab3= st.tabs([ "Total Sales","Quantity", " Data"])

trend_all = monthly_trend(df)
trend_p = trend_platform(df)

with tab1:
    st.markdown("### Tren Penjualan per Platform")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_total = px.line(
            trend_all,
            x="year_month",
            y="total_sales",
            markers=True,
            title="Trend Total Penjualan"
        )
        st.plotly_chart(fig_total, use_container_width=True)
        
    with col2:
        fig_qty = px.line(
            trend_p,
            x="year_month",
            y="total_sales",
            color="platform",
            markers=True,
            title="Total Sales per Platform"
        )

        st.plotly_chart(fig_qty, use_container_width=True)
        
    
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Quantity Bulanan")

        fig = px.line(
            trend_all,
            x="year_month",
            y="quantity",
            markers=True,
            title="Trend Quantity"
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 QUANTITY TREND
    with col2:
        st.markdown("### Total Produk Bulanan")

        fig = px.line(
            trend_p,
            x="year_month",
            y="quantity",
            color="platform",
            markers=True,
            title="Trend Quantity Per Platform"
        )

        st.plotly_chart(fig, use_container_width=True)

    # 🔹 PER PLATFORM
    

with tab3:
    st.markdown("### Data Trend")
    st.dataframe(trend_all)

st.divider()

# ======================
# CATEGORY ANALYSIS
# ======================
st.subheader("Analisis Kategori Produk")

tab1, tab2, tab3= st.tabs(["Total Sales", " Quantity", "Data"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        data_sel = category_sales(df).reset_index()

        fig = px.bar(
            data_sel,
            x="product_category",
            y="total_sales",
            title="Total Penjualan per Kategori",
            color="product_category"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        data_plat_sel = category_sales_platform(df).reset_index()

        fig = px.bar(
            data_plat_sel,
            x="product_category",
            y="total_sales",
            color="platform",
            barmode="group",
            title="Total Penjualan Kategori per Platform"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        data_qty = category_quantity(df).reset_index()

        fig = px.bar(
            data_qty,
            x="product_category",
            y="quantity",
            title="Penjualan Kategori",
            color="product_category"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
# 🔹 QUANTITY PER CATEGORY
        data_plat_qty = category_quantity_platform(df).reset_index()

        fig = px.bar(
            data_plat_qty,
            x="product_category",
            y="quantity",
            color="platform",
            barmode="group",
            title="Penjualan Kategori per Platform"
        )


        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(data_plat_sel)

st.divider()

st.subheader("Analisis Kategori Produk Per Bulan")

tab1, tab2, tab3= st.tabs(["Total Sales", " Quantity", "Data"])
with tab1:
    cat_month = category_monthly(df)

    fig = px.line(
        cat_month,
        x="year_month",
        y="total_sales",
        color="product_category",
        markers=True,
        title="Kategori per Bulan"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    cat_month_p = category_monthly_platform(df)

    fig = px.line(
        cat_month_p,
        x="year_month",
        y="total_sales",
        color="product_category",
        facet_col="platform",
        markers=True,
        title="Kategori per Bulan per Platform"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(cat_month)

st.divider()
# ======================
# DISCOUNT EFFECT
# ======================
col1, col2 = st.columns(2)
with col1:
    st.subheader("Penjualan Harian")

    day_sales = sales_per_day(df).reset_index()

    fig = px.bar(
        day_sales,
        x="day_name",
        y="total_sales",
        title="Penjualan Berdasarkan Hari"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Discount vs Sales")

    df_scatter = discount_effect(df)

    if not df_scatter.empty:
        fig = px.scatter(
            df_scatter,
            x="discount",
            y="total_sales",
            color="platform"
        )

        fig.update_yaxes(type="log")  # biar kebaca (data skew)
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