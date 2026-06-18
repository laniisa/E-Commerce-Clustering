import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from modules.auth_check import *
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

load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/eda.css"
)
check_login()
show_sidebar("eda")


# LOAD DATA

st.title("Exploratory Data Analysis")

st.markdown(f"""
<div class="alert-box">
    <div class="alert-desc">
        Exploratory Data Analysis (EDA) menampilkan proses eksplorasi data untuk memahami karakteristik, distribusi, tren penjualan, serta hubungan antar variabel pada dataset penjualan.
    </div>
</div>
""", unsafe_allow_html=True)


if "integrated" not in st.session_state:
    st.warning("Silahkan lakukan preprocessing terlebih dahulu!")
    st.stop()

df = st.session_state.integrated.copy()
st.session_state.data_original = df.copy()
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

# OVERVIEW

info = get_overview(df)

m1,m2,m3,m4 = st.columns(4)
metric_data = [
    ("Total Data", info["total_data"]),
    ("Total Produk", info["total_product"]),
    ("Jumlah Platform", info["total_platform"]),
    ("Periode Awal", info["min_date"].date())
]

for col,item in zip([m1,m2,m3,m4], metric_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{item[0]}</div>
            <div class="metric-value">{item[1]}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()


# DESCRIPTIVE

col1, col2 = st.columns(2)
with col1:
    st.subheader(" ▶ Statistik Deskriptif")
    
    st.dataframe(
        descriptive_stats(df, num_cols),use_container_width=True,height=350)
with col2:
    st.subheader("▶ Platform Performance")
    platform_data = platform_contribution(df)
    tab1, tab2, tab3 = st.tabs(["Transaksi", "Total Sales", "Data"])
    with tab1:
        fig2 = px.bar(
            platform_data,
            x="platform",
            y="total_transaksi",
            color="platform"
        )
        st.plotly_chart(fig2, use_container_width=True, height=300, key="perf1")
    
    with tab2:
        fig1 = px.bar(
            platform_data,
            x="platform",
            y="total_sales",
            color="platform"
        )
        st.plotly_chart(fig1, use_container_width=True, height=300, key="perf2")
    with tab3:
        st.dataframe(platform_data, use_container_width=True)
    
st.divider()

# DISTRIBUSI

st.subheader("▶ Distribusi Data Awal")
st.info("Menunjukkan pola distribusi data awal untuk melihat tingkat skewness, persebaran data, serta keberadaan outlier sebelum proses clustering dilakukan.")

col_dis = st.selectbox("Pilih Variabel", num_cols)
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(
        df,
        x=col_dis,
        marginal="box",
        title=f"Distribusi {col_dis} global",
    )
    st.plotly_chart(fig, use_container_width=True, key="dist1")
with col2:    
    fig = px.histogram(
        df,
        x=col_dis,
        color="platform",
        marginal="box",
        title=f"Distribusi {col_dis} per platform",
    )
    st.plotly_chart(fig, use_container_width=True, key="dist2")


st.divider()

#INFO

diagnosis_text, detail_df, rekom = generate_data_diagnosis(df, num_cols)

if rekom == "Log":\
    st.info(f"{diagnosis_text} Sistem merekomendasikan transformasi logaritmik untuk menstabilkan distribusi data sebelum clustering.")
else:
    st.success("Distribusi data sudah cukup stabil. Transformasi data bersifat opsional.")

b1, b2 = st.columns(2)

with b1:
    if st.button("Gunakan Transformasi Logaritmik", use_container_width=True):
        st.session_state.data_ready = log_transform(df)
        st.session_state.data_original = df.copy()
        st.session_state.is_log_transform = True
        st.success(f"Berhasil dilakukan Transformasi Logaritmik.")

with b2:
    if st.button("Gunakan Data Asli", use_container_width=True):
        st.session_state.data_ready = df.copy()
        st.session_state.data_original = df.copy()
        st.success("Data asli digunakan tanpa transformasi.")

#SETELAH LOG TRANSFORM
if st.session_state.get("is_log_transform", False):
    df_norm = st.session_state.data_ready
    
    st.divider()
    st.subheader("▶ Distribusi Setelah Transformasi Logaritmik")
    st.info("Menampilkan perubahan distribusi data setelah transformasi logaritmik sehingga distribusi data menjadi lebih stabil dan pengaruh outlier dapat dikurangi.")

    norm_col = st.selectbox("Pilih Variabel", num_cols, key="norm")
    nor1,nor2 = st.columns(2)
    with nor1:
        fig = px.histogram(df_norm, x=norm_col, marginal="box", title="Distribusi Global")
        st.plotly_chart(fig, use_container_width=True, key="norm1")

    with nor2:
        fig = px.histogram(df_norm, x=norm_col, color="platform", marginal="box", title="Distribusi per Platform")
        st.plotly_chart(fig, use_container_width=True, key="norm2")

    
    # DIAGNOSA SETELAH LOG
    
    before_check = get_skew_outlier(df, num_cols)
    after_check = get_skew_outlier(df_norm, num_cols)

    before_skew = round(before_check["Skewness"].mean(), 3)
    after_skew = round(after_check["Skewness"].mean(), 3)

    before_out = round(before_check["Persentase (%)"].mean(), 2)
    after_out = round(after_check["Persentase (%)"].mean(), 2)

    st.success(f"""
    Transformasi logaritmik berhasil menurunkan rata-rata skewness data
    dari {before_skew} menjadi {after_skew} serta menurunkan rata-rata
    persentase outlier dari {before_out}% menjadi {after_out}%.
    Distribusi data menjadi lebih stabil untuk proses clustering.
    """)

    st.divider()

# CORRELATION

st.subheader("▶ Matriks Korelasi")
st.info("Menunjukkan hubungan antar variabel numerik untuk melihat keterkaitan antar fitur pada dataset.")
kor1, kor2, kor3 = st.columns([1,4,1])

with kor2:
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(
        correlation_matrix(df, num_cols),
        annot=True,
        cmap="coolwarm",
        ax=ax
    )
    st.pyplot(fig)

st.divider()


st.subheader("▶ Matriks Korelasi per Platform")
corrs = corr_per_platform(df, num_cols)

cols = st.columns(len(corrs))
for i, (p, corr) in enumerate(corrs.items()):
    with cols[i]:
        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.caption(p)
        st.pyplot(fig)

st.divider()


# TREND ANALYSIS

st.subheader("▶ Analisis Tren Penjualan")
st.info("Menampilkan pola perubahan total penjualan dan jumlah produk terjual dari waktu ke waktu, baik secara keseluruhan maupun berdasarkan platform.")

tab1, tab2, tab3= st.tabs([ "Total Sales","Quantity", " Data"])

trend_all = monthly_trend(df)
trend_p = trend_platform(df)

with tab1:
    st.markdown("Tren Penjualan Berdasarkan Total Sales")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_total = px.line(
            trend_all,
            x="year_month",
            y="total_sales",
            markers=True,
            title="Trend Total Penjualan Keseluruhan"
        )
        st.plotly_chart(fig_total, use_container_width=True, key="trend1")
        
    with col2:
        fig_qty = px.line(
            trend_p,
            x="year_month",
            y="total_sales",
            color="platform",
            markers=True,
            title="Total Sales per Platform"
        )

        st.plotly_chart(fig_qty, use_container_width=True, key="trend2")
        
    
with tab2:
    col1, col2 = st.columns(2)
    st.markdown("Tren Penjualan Berdasarkan Quantity")

    with col1:
        fig = px.line(
            trend_all,
            x="year_month",
            y="quantity",
            markers=True,
            title="Trend Quantity Keseluruhan"
        )

        st.plotly_chart(fig, use_container_width=True, key="trend3")

    
    with col2:

        fig = px.line(
            trend_p,
            x="year_month",
            y="quantity",
            color="platform",
            markers=True,
            title="Trend Quantity Per Platform"
        )

        st.plotly_chart(fig, use_container_width=True, key="trend4")
    

with tab3:
    st.markdown("### Data Trend")
    st.dataframe(trend_all)

st.divider()


# product ANALYSIS

st.subheader("▶ Analisis Produk")
st.info("Menampilkan kontribusi masing-masing produk terhadap penjualan berdasarkan total penjualan dan jumlah produk terjual pada setiap platform.")

tab1, tab2, tab3= st.tabs(["Total Sales", " Quantity", "Data"])
max = df["product_name"].nunique()
with tab1:
    top_n = st.slider(
            "Jumlah Top Produk",
            min_value=5,
            max_value=max,
            value=min(20, max),
            key="top_sales"
        )
    col1, col2 = st.columns(2)
    with col1:
        data_sales = product_sales(df, top_n)
        fig = px.bar(
            data_sales,
            x="total_sales",
            y="product_name",
            orientation="h",
            color="total_sales",
            title=f"Top {top_n} Produk Berdasarkan Total Sales Keseluruhan"
        )
        st.plotly_chart(fig,use_container_width=True,key="cat1")

    with col2:
        data_sales_plat = product_sales_platform(df, top_n)
        fig = px.bar(
            data_sales_plat,
            x="product_name",
            y="total_sales",
            color="platform",
            barmode="group",
            title="Produk Berdasarkan Total Sales per Platform"
        )

        fig.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig,use_container_width=True,key="cat2")


# QUANTITY

with tab2:
    
    top_qty = st.slider(
            "Jumlah Top Quantity",
            min_value=5,
            max_value=max,
            value=min(20, max),
            key="top_qty"
        )
    
    col1, col2 = st.columns(2)

    with col1:

        data_qty = product_quantity(df, top_qty)

        fig = px.bar(
            data_qty,
            x="quantity",
            y="product_name",
            orientation="h",
            color="quantity",
            title=f"Top {top_qty} Produk Berdasarkan Quantity Keseluruhan"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="cat3"
        )

    with col2:

        data_qty_plat = product_quantity_platform(df, top_qty)

        fig = px.bar(
            data_qty_plat,
            x="product_name",
            y="quantity",
            color="platform",
            barmode="group",
            title="Produk Berdasarkan Quantity per Platform"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="cat4"
        )


# DATA

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.write("Data Total Sales")
        st.dataframe(product_sales(df, top_n))
    with col2:
        st.write("Data Quantity")
        st.dataframe(product_quantity(df, top_qty))


st.divider()

# PRODUK PER BULAN

st.subheader("▶ Analisis Tren Produk")
st.info("Menunjukkan perubahan tren penjualan produk setiap bulan serta perbedaan kontribusi penjualan pada masing-masing platform e-commerce.")
tab1, tab2, tab3= st.tabs(["Global", " Platform ", "Data"])

with tab1:
    top_month = st.slider(
        "Jumlah Produk Trend",
        min_value=5,
        max_value=max,
        value=min(20, max),
        key="trend_top"
    )
    cat_month = product_monthly(df, top_month)
    fig = px.line(
        cat_month,
        x="year_month",
        y="total_sales",
        color="product_name",
        markers=True,
        title=f"Trend Top {top_month} Produk per Bulan Keseluruhan"
    )
    st.plotly_chart(fig,use_container_width=True,key="cat5")

# PLATFORM
with tab2:

    cat_month_p = product_monthly_platform(df, top_month)

    fig = px.line(
        cat_month_p,
        x="year_month",
        y="total_sales",
        color="product_name",
        facet_col="platform",
        markers=True,
        title="Trend Produk per Platform"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="cat6"
    )


# DATA

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.write("Produk per Bulan")
        st.dataframe(cat_month)

    with col2:
        st.write("Produk per Bulan antar Platform")
        st.dataframe(cat_month_p)

st.divider()

# DISKON

st.subheader("▶ Analisis Tren Diskon Penjualan")
st.info("Menampilkan tren perubahan diskon dari waktu ke waktu untuk melihat pola pemberian diskon secara keseluruhan maupun berdasarkan platform.")
tab1, tab2 = st.tabs(["Visual", "Data"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=trend_all["year_month"],
                y=trend_all["total_sales"],
                name="Total Sales"
            ),secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=trend_all["year_month"],
                y=trend_all["discount"],
                mode="lines+markers",
                name="Discount"
            ),secondary_y=True
        )
        fig.update_layout( title="Trend Discount terhadap Total Sales Keseluruhan")
        fig.update_yaxes(title_text="Total Sales", secondary_y=False)
        fig.update_yaxes(title_text="Average Discount", secondary_y=True)

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for platform in trend_p["platform"].unique():
            data = trend_p[trend_p["platform"] == platform]
            fig.add_trace(
                go.Scatter(
                    x=data["year_month"],
                    y=data["total_sales"],
                    mode="lines+markers",
                    name=f"{platform} - Sales"
                ), secondary_y=False
            )
            fig.add_trace(
                go.Scatter(
                    x=data["year_month"],
                    y=data["discount"],
                    mode="lines",
                    line=dict(dash="dot"),
                    name=f"{platform} - Discount"
                ),secondary_y=True
            )
        fig.update_layout(title="Trend Discount dan Total Sales Per Platform",hovermode="x unified")
        fig.update_yaxes(title_text="Total Sales",secondary_y=False)
        fig.update_yaxes(title_text="Average Discount",secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        
        
with tab2:
    st.write("Tren Diskon per Bulan ")
    st.dataframe(trend_all)


st.divider()



col1, col2, col3 = st.columns([1, 6 ,1])

with col1:
    if st.button("⬅️ Kembali", use_container_width=True):
        st.switch_page("pages/5_preprocessing.py")

with col3:
    if st.button("➡️ Lanjut", use_container_width=True):
        st.switch_page("pages/7_clustering.py")