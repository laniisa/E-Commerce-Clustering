import pandas as pd
import re
import streamlit as st
import numpy as np

\
# ======================
# CLEANING
# ======================
def clean_data(df, platform):

    platform = platform.lower()

    if platform == "shopee":
        df["Returned quantity"] = pd.to_numeric(df["Returned quantity"], errors="coerce")

        df = df[
            (df["Status Pesanan"] == "Selesai") &
            (df["Alasan Pembatalan"].isna()) &
            (df["Status Pembatalan/ Pengembalian"].isna()) &
            (
                df["Returned quantity"].isna() |
                (df["Returned quantity"] == 0)
            )
        ]

    elif platform == "lazada":
        df["refundAmount"] = pd.to_numeric(df["refundAmount"], errors="coerce")

        df = df[
            (df["status"] == "confirmed") &
            (df["buyerFailedDeliveryReturnInitiator"].isna()) &
            (df["buyerFailedDeliveryReason"].isna()) &
            (
                df["refundAmount"].isna() |
                (df["refundAmount"] == 0)
            )
        ]

    elif platform == "tiktok":
        df["Order Refund Amount"] = pd.to_numeric(df["Order Refund Amount"], errors="coerce")

        df = df[
            (df["Order Status"] == "Selesai") &
            (df["Order Substatus"] == "Selesai") &
            (df["Cancelation/Return Type"].isna()) &
            (
                df["Order Refund Amount"].isna() |
                (df["Order Refund Amount"] == 0)
            ) &
            (df["Cancel Reason"].isna())
        ]

    return df


# ======================
# SELECTION
# ======================
def select_columns(df, platform):

    platform = platform.lower()

    if platform == "shopee":
        return df[[
            "Nama Produk", "Harga Awal", "Total Diskon",
            "Jumlah", "Total Harga Produk", "Waktu Pesanan Dibuat"
        ]]

    elif platform == "lazada":
        return df[[
            "itemName", "unitPrice", "sellerDiscountTotal",
            "bundleDiscount", "paidPrice", "createTime"
        ]]

    elif platform == "tiktok":
        return df[[
            "Product Name", "SKU Unit Original Price",
            "SKU Seller Discount", "SKU Platform Discount",
            "Quantity", "SKU Subtotal After Discount", "Created Time"
        ]]

    return df

# ======================
# CLEAN PRODUCT NAME
# ======================
def product_desc(name):
    if pd.isna(name):
        return name

    name = str(name).lower()

    name = re.sub(r"\(.*?\)|\[.*?\]|\!", "", name)
    parts = re.split(r"[-,/.]", name, maxsplit=2)

    main_part = parts[0].strip()
    if len(main_part.split()) < 2 and len(parts) > 1:
        main_part = parts[1].strip()

    promo_words = [
        'promo','murah','diskon','gratis','free','harga',
        'best seller','new','premium', 'quality', 'high', 'original', 'import',
        'khusus', 'pesanan', 'promosikan'
    ]

    for w in promo_words:
        main_part = re.sub(rf'\b{w}\b', '', main_part)

    return re.sub(r'\s+', ' ', main_part).strip().title()


# ======================
# CATEGORY
# ======================
def product_category(desc):
    desc = str(desc).lower()

    rules = {
        "Paket Kain": ["paket", "bridesmaid", "set kain", "set"],
        "Renda": ["renda"],
        "Kain Beludru": ["beludru", "bludru"],
        "Kain Songket": ["songket"],
        "Kain Tile": ["tile", "tulle", "tille"],
        "Kain Velvet": ["velvet"],
        "Kain Maxmara": ["maxmara"],
        "Kain Armani": ["armani", "armany"],
        "Kain Roberto": ["roberto"],
        "Kain Bridal": ["bridal"],
        "Kain Sequin": ["sequin", "payet", "squeen", "background", "backdrop"],
        "Kain Organza": ["organza"],
        "Kain Jacquard": ["fukuro", "jacquard", "janggan"],
        "Kain Brokat": ["brokat", "brukat"],
        "Kain Shimmer Silk": ["shimer", "shimmer"],
        "Kain Silk Gradasi": ["gradasi"],
        "Kain Katun": ["katun"],
        "Kain Linen": ["linen"],
        "Kain Drill": ["drill"],
        "Kain Batik": ["batik"],
        "Toyobo": ["toyobo"],
        "Kain Crinkle": ["crinkle"],
        "Kain Corduroy": ["corduroy"],
        "Kain Cheongsam": ["cheongsam", "congsam"],
        "Kain Hero": ["hero"],
        "Others" : []
     }

    for cat, keywords in rules.items():
        for kw in keywords:
            if kw in desc:
                return cat

    return "Others"


# ======================
# CLEANING FUNCTION
# ======================
def clean_shopee(x):
    if pd.isna(x):
        return None
    try:
        x = str(x).strip()

        # format ribuan (3.694.000)
        if x.count(".") > 1:
            return float(x.replace(".", ""))

        x = float(x)

        # desimal → rupiah
        if x < 1000:
            return x * 1000

        return x

    except:
        return None


def clean_discount(x):
    if pd.isna(x):
        return 0
    try:
        x = str(x).strip()

        # format ribuan
        if x.count(".") > 1:
            return float(x.replace(".", ""))

        return float(x)

    except:
        return 0

# ======================
# FIX PRICE (ROBUST)
# ======================
def fix_price(row):
    price = row["price"]
    qty = row["quantity"]
    total = row["total_sales"]

    if pd.isna(price) or pd.isna(total):
        return price

    if price * qty > total:
        if (price/10)*qty == total:
            return price/10
        elif (price/100)*qty == total:
            return price/100
        elif (price/1000)*qty == total:
            return price/1000

    return price


# ======================
# FIX DISCOUNT
# ======================
def fix_discount(row):
    price = row["price"]
    qty = row["quantity"]
    discount = row["discount"]
    total = row["total_sales"]

    if pd.isna(price) or pd.isna(total):
        return discount

    base = price * qty

    candidates = [
        discount,
        discount * 1000,
        discount / 1000
    ]

    for d in candidates:
        if abs((base - d) - total) < 1:
            return d

    return discount

# ===================
# PRODUCT CODE
# ===================
def generate_product_code(df, prefix):
    product_master = (
        df[["product_desc", "product_category"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    product_master["product_code"] = [
        f"{prefix}-{str(i+1).zfill(5)}"
        for i in range(len(product_master))
    ]

    # merge kembali ke dataframe utama
    df = df.merge(
        product_master,
        on=["product_desc", "product_category"],
        how="left"
    )

    return df, product_master

# ======================
# TRANSFORM (STANDARDIZE)
# ======================
def transform_data(df, platform):

    platform = platform.lower()
    prefix_map = {
        "shopee": "SH",
        "lazada": "LZ",
        "tiktok": "TK"
    }
    prefix = prefix_map.get(platform, "OT")
    # ======================
    # MAPPING KOLOM
    # ======================
    if platform == "shopee":
        df = df.rename(columns={
            "Nama Produk": "product_name",
            "Harga Awal": "price",
            "Total Diskon": "discount",
            "Jumlah": "quantity",
            "Total Harga Produk": "total_sales",
            "Waktu Pesanan Dibuat": "transaction_date"
        })

    elif platform == "lazada":
        df["discount"] = (
            df["sellerDiscountTotal"].fillna(0) +
            df["bundleDiscount"].fillna(0)
        ).abs()

        df = df.rename(columns={
            "itemName": "product_name",
            "unitPrice": "price",
            "paidPrice": "total_sales",
            "createTime": "transaction_date"
        })

        df["quantity"] = 1

    elif platform == "tiktok":
        df["discount"] = (
            df["SKU Seller Discount"].fillna(0) +
            df["SKU Platform Discount"].fillna(0)
        )

        df = df.rename(columns={
            "Product Name": "product_name",
            "SKU Unit Original Price": "price",
            "Quantity": "quantity",
            "SKU Subtotal After Discount": "total_sales",
            "Created Time": "transaction_date"
        })

    # ======================
    # FEATURE ENGINEERING
    # ======================
    df["product_desc"] = df["product_name"].apply(product_desc)
    df["product_category"] = df["product_desc"].apply(product_category)

    # ======================
    # CLEAN NUMERIC
    # ======================
    if platform.lower() == "shopee":
        df["price"] = df["price"].apply(clean_shopee)
        df["discount"] = df["discount"].apply(clean_discount)
        df["total_sales"] = df["total_sales"].apply(clean_shopee)
    # ===============================
    # CONVERT NUMERIC
    # ===============================
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
    df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce")

    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date

    # ======================
    # HANDLE MISSING TOTAL
    # ======================
    df["total_sales"] = df["total_sales"].fillna(
        df["price"] * df["quantity"] - df["discount"]
    )

    # ======================
    # FIX ERROR DATA
    # ======================
    df["price"] = df.apply(fix_price, axis=1)
    df["discount"] = df.apply(fix_discount, axis=1)

    # ======================
    # PRODUCT CODE
    # ======================
    df, product_master = generate_product_code(df, prefix)

    # ======================
    # FINAL CLEAN
    # ======================
    df = df[[
        "product_code",
        "product_desc",
        "product_category",
        "price",
        "discount",
        "quantity",
        "total_sales",
        "transaction_date"
    ]]

    df["platform"] = platform.capitalize()

    return df

# ======================
# INTEGRATION
# ======================
def integrate_data(dfs):
    return pd.concat(dfs, ignore_index=True)


def dataset_overview(dfs):
    total_rows = sum(df.shape[0] for df in dfs)
    total_cols = sum(df.shape[1] for df in dfs)
    total_missing = sum(df.isna().sum().sum() for df in dfs)

    return total_rows, total_cols, total_missing


def show_quality(df):
    missing = df.isna().sum().sum()

    if missing == 0:
        st.success("✅ Tidak ada missing value")
    else:
        st.warning(f"⚠️ Missing value: {missing}")

def show_summary(df, file_name, platform):
    color = get_platform_color(platform)

    st.markdown(f"""
    <div style="
        border-left: 6px solid {color};
        padding: 12px;
        border-radius: 10px;
        background: #f9fafb;
        margin-bottom: 10px;
        border: 1px solid #e5e7eb;
    ">
        📄 <b>{file_name}</b><br>
        🏷️ Platform: <span style="color:{color}; font-weight:600;">{platform.capitalize()}</span><br>
        Rows: {df.shape[0]} | Columns: {df.shape[1]}
    </div>
    """, unsafe_allow_html=True)

def get_platform_color(platform):
    platform = str(platform).lower()

    if platform == "shopee":
        return "#ff6a00"   # orange
    elif platform == "lazada":
        return "#4b2cff"   # ungu-biru
    elif platform == "tiktok":
        return "#000000"   # hitam
    return "#6b7280"       # default abu