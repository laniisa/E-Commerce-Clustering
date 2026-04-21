import streamlit as st
from modules.auth_check import check_login, load_css
from components.sidebar import show_sidebar

load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css"
)
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)
check_login()
show_sidebar("panduan")

st.title("📘 Panduan Penggunaan Aplikasi")

st.markdown("""
Panduan langkah-langkah penggunaan sistem analisis penjualan multi-platform Exploratory Data Analisys dan clustering K-Medoids
""")

st.divider()

# ======================
# STEP 1 - UPLOAD
# ======================
st.header("1️⃣ Upload Dataset")

st.markdown("""
Pengguna mengisi nama dataset 
Pengguna dapat mengunggah dataset untuk dianalisis dengan ketentuan:

- Dapat mengunggah lebih dari satu file (multi-platform)
- Format file: `.csv` atau `.xlsx`
- Nama file harus mengandung nama platform  
  *(contoh: data_shopee.csv, penjualan_lazada.xlsx)*
- Platform yang didukung: **Shopee, Lazada, dan TikTok Shop**

Setelah berhasil diunggah, data akan ditampilkan untuk ditinjau.
""")


st.divider()

# ======================
# STEP 2 - PREPROCESSING
# ======================
st.header("2️⃣ Preprocessing Data")

st.markdown("""
Pada tahap ini sistem akan melakukan:

- **Cleaning Data** → pembersihan data dengan hasil data benar valid penjualan selesai  
- **Selection Data** → memilih atribut yang digunakan  
- **Transformation Data** → mengubah format data (misalnya tanggal)  
- **Integration Data** → menggabungkan data dari berbagai platform  

""")
st.divider()

# ======================
# STEP 3 - EDA
# ======================
st.header("3️⃣ Exploratory Data Analysis (EDA)")

st.markdown("""
Pada tahap ini, pengguna dapat mengeksplorasi data melalui:

- Statistik deskriptif
- Distribusi data
- Deteksi outlier dan penanganan outlier dengan Log Transformation da RobustScaller
- Korelasi antar variabel
- Tren penjualan (bulanan & per platform)
- Analisis kategori produk
- Analisis pengaruh diskon terhadap penjualan

""")

st.divider()

# ======================
# STEP 4 - NORMALISASI
# ======================
st.header("4️⃣ Clustering K-Medoids")

st.markdown("""
Proses clustering dilakukan menggunakan algoritma **K-Medoids**.

Langkah:
- Pengguna dapat menentukan jumlah cluster (k):
  - Otomatis menggunakan **Silhouette Score**
  - Manual (input nilai k)
- Mengelompokkan data berdasarkan kemiripan menggunakan jarak Euclidean  

 Dengan Output:
- Label cluster untuk setiap data
- Pembagian kelompok produk
- Data dengan label cluster
- Visualisasi cluster
- Ringkasan karakteristik tiap cluster
Pengguna dapat mengunduh hasil clustering dalam format: `.csv`


""")

st.divider()

# ======================
# NAVIGATION
# ======================
col1, col2, col3 = st.columns([1,6,1])

with col3:
    if st.button("➡️ Mulai", use_container_width=True):
        st.switch_page("pages/4_upload_data.py")