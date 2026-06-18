import streamlit as st
from modules.auth_check import *
from components.sidebar import show_sidebar

load_icons()
load_css(
    "assets/style/style.css",
    "assets/style/sidebar.css",
    "assets/style/dashboard.css"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display:none;}
</style>
""", unsafe_allow_html=True)

check_login()
show_sidebar("panduan")

st.title("Panduan Penggunaan Aplikasi")

st.markdown("""
Halaman ini berisi panduan penggunaan sistem analisis penjualan multi-platform 
berbasis **Exploratory Data Analysis (EDA)** dan **Clustering K-Medoids**.  
Pengguna dapat mengikuti tahapan berikut secara berurutan agar proses analisis berjalan optimal.
""")

st.divider()

st.header("1. Upload Dataset")

st.markdown("""
Pengguna terlebih dahulu menginput nama dataset kemudian mengunggah file data penjualan yang akan dianalisis.

Dengan Ketentuan Upload:
- Mendukung upload lebih dari satu file (**multi-platform**)
- Format file yang diterima: `.csv` atau `.xlsx`
- Nama file harus mengandung identitas platform:`shopee`, `lazada`, `tiktok`
- Dataset yang diunggah harus berupa data transaksi penjualan.
""")
st.divider()

st.header("2. Preprocessing Data")

st.markdown("""
Pada tahap preprocessing, sistem melakukan penyiapan data agar seluruh dataset dari berbagai platform memiliki struktur yang seragam dan siap dianalisis.

Proses yang dilakukan sistem:

a. Cleaning Data
Menghapus data transaksi yang:batal, retur, refund, atau tidak berstatus transaksi selesai.

b. Selection Data
Sistem menyeleksi atribut yang relevan terhadap analisis penjualan, yaitu: nama produk, harga, diskon, quantity, total penjualan, tanggal transaksi.

c. Transformation Data
Sistem melakukan penyamaan nama kolom multi-platform, pembersihan format numerik,

d. Integration Data
Menggabungkan seluruh data hasil transform menjadi satu dataset terintegrasi.

""")

st.divider()

st.header("3. Exploratory Data Analysis (EDA)")

st.markdown("""
Tahap EDA digunakan untuk memahami karakteristik data sebelum dilakukan clustering.

Analisis yang disediakan:
- Statistik deskriptif data numerik
- Distribusi data per variabel
- Matriks korelasi antar variabel
- Trend Penjualan
- Trend kategori produk

Diagnosa Kondisi Data
Pada tahap ini sistem akan memeriksa:
- pola distribusi data numerik,
- tingkat kemencengan distribusi (skewness),
- persentase outlier.

Berdasarkan hasil diagnosa tersebut, sistem akan memberikan rekomendasi apakah data perlu dilakukan Log Transformation atau tidak.

Log Transformation digunakan untuk membantu:
- mereduksi distribusi data yang terlalu melebar,
- menurunkan efek skewness,
- mengurangi pengaruh nilai ekstrem.

Jika kondisi data masih relatif stabil, maka penggunaan Log Transformation bersifat opsional sesuai kebutuhan pengguna.

""")

st.divider()

st.header("4. Clustering K-Medoids")

st.markdown("""
Tahap ini merupakan proses utama pengelompokan data penjualan menggunakan algoritma **K-Medoids**.

Penentuan Jumlah Cluster (K)
Pengguna dapat menentukan jumlah cluster dengan dua cara:

Otomatis
Sistem menghitung beberapa nilai K menggunakan **Silhouette Score**, lalu memilih nilai terbaik.
Silhouette Score digunakan untuk mengukur kualitas pemisahan cluster:
- 0.70 – 1.00 → Strong Structure
- 0.51 – 0.69 → Reasonable Structure
- 0.26 – 0.50 → Weak Structure
- ≤ 0.25 → No Substantial Structure

Manual
Pengguna dapat menginput nilai K sendiri, dan sistem tetap akan menghitung nilai evaluasi cluster.

Evaluasi Hasil Clustering
Setelah clustering selesai, sistem menampilkan:

Davies Bouldin Index (DBI)
Menunjukkan tingkat kemiripan antar cluster.
Semakin kecil nilai DBI → cluster semakin terpisah dengan baik.

Visualisasi dan Output
Sistem akan menghasilkan:
- visualisasi persebaran cluster (PCA),
- distribusi jumlah data per cluster,
- persebaran platform per cluster,
- detail data tiap cluster,
- interpretasi karakteristik cluster.

Selain itu pengguna dapat:
- menyimpan hasil clustering ke database,
- mengunduh hasil clustering dalam format Excel.
""")

st.divider()

col1, col2, col3 = st.columns([1,6,1])

with col3:
    if st.button("➡️ Mulai Analisis", use_container_width=True):
        st.switch_page("pages/4_upload_data.py")