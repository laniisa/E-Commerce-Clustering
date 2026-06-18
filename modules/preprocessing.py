import pandas as pd
import re
import streamlit as st
from num2words import num2words
from rapidfuzz import fuzz
from word2number import w2n
import numpy as np


# CLEANING

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



# SELECTION

def select_columns(df, platform):

    platform = platform.lower()

    if platform == "shopee":
        return df[[
            "No. Pesanan", "Nama Produk", "SKU Induk", "Harga Awal", "Total Diskon",
            "Jumlah", "Total Harga Produk", "Waktu Pesanan Dibuat"
        ]]

    elif platform == "lazada":
        return df[[
            "orderNumber", "itemName", "sellerSku", "unitPrice", 
            "sellerDiscountTotal", "bundleDiscount", "paidPrice", "createTime"
        ]]

    elif platform == "tiktok":
        return df[[
            "Order ID", "Product Name", "SKU ID", "SKU Unit Original Price",
            "SKU Seller Discount", "SKU Platform Discount",
            "Quantity", "SKU Subtotal After Discount", "Created Time"
        ]]

    return df


# PEMBERSIHAN PRODUCT NAME

def clean_product_name(name):
    if pd.isna(name):
        return name

    name = str(name).lower()

    #ambil split awal
    parts = re.split(r"\s*[-/,|]\s*", name, maxsplit=1)
    main_part = parts[0].strip()

    if len(main_part.split()) < 2 and len(parts) > 1:
        main_part = main_part + " " + parts[1].strip()
    
    name = main_part.split(",")[0]

    #hapus kurung
    name = re.sub(r"\(.*?\)|\[.*?\]|\!", "", name)
    
    #hapus karakter
    name = re.sub(r"[^\w\s&]", " ", name)
    
    
    #huruf berulang
    name = re.sub(r'([a-zA-Z])\1{2,}', r'\1', name)

    # ubah 3 5 -> 3.5
    name = re.sub(r'(\d)\s+(\d)', r'\1.\2', name)

    name = re.sub(r'\bwarna\b.*$', '', name)

    color_patterns = [
        r"burgundy",
        r"emerald(?: blue)?",
        r"denim(?: blue)?",
        r"baby blue",
        r"sage green",
        r"coklat mahogany",
        r"taro mauve",

        r"burgundy",
        r"emerald",
        r"denim",
        r"mahogany",
        r"rosegold",
        r"maroon",
        r"hitam",
        r"putih",
        r"silver",
        r"blue",
        r"green",
    ]
    color_patterns = sorted(color_patterns, key=len, reverse=True)

    pattern = r"\b(?:%s)\b" % "|".join(color_patterns)

    name = re.sub(pattern, "", name)

    # rapihin spasi
    name = re.sub(r"\s+", " ", name).strip()
    stopwords = {
        # marketing
        "premium",
        "quality",
        "high",
        "elegant",
        "best",
        "murah",
        "promo",
        "diskon",
        "gratis",
        "free",
        "new",
        "khusus",
        "tebal",
        "spesial",
        "package",
        "promokain",
        "pesanan",
        "dress",
        "warna",
        "polos",
        "cantik",
        "modern",
        "meteran",
        "mewah",
        "ombre",
        "dan",
        "original",
        "import",
        "terbaru",
        "seller",
        "harga",
        "grosir",
        "siap",
        "pakai",
        "kain",
        "bahan",
        "halus",
        "lux",
        "luxury",
        "dekorasi",

    }
    
    
    tokens = name.split()
    indo_number = {
        'satu': '1',
        'dua': '2',
        'tiga': '3',
        'seribu': '1000',
    }
    replace_dict = {
        "brukat": "brokat",
        "bludru": "beludru",
        "shimer": "shimmer",
        "squeen": "sequin",
        "sequins": "sequin",
        "tille": "tile",
        "tulle": "tile",
        "armany": "armani",
        "armanyy": "armani",
        "maxmaraa": "maxmara",
        "cavali": "cavalli",
        "congsam": "cheongsam",
        "embos": "emboss",
        "songkett": "songket",
        "bridesmaids": "bridesmaid",
        "aksesoris": "aksesori",
        "furring": "furing",
        "payettt": "payet",
        "brugundy": "burgundy",
        "brogandy": "burgundy",
        "cina": "",
        "junior": "",

    }

    normalized_tokens = []

    for token in tokens:

        # word number normalize
        try:
            token = str(w2n.word_to_num(token))
        except:
            pass
        
        token = replace_dict.get(token, token)

        if token in stopwords:
            continue

        if token in ["i", "ii", "iii", "iv", "v"]:
            continue

        token = indo_number.get(token, token)

        if token.strip() == "":
            continue

        normalized_tokens.append(token)
    
    unique_tokens = []
    seen = set()

    for token in normalized_tokens:
        if token not in seen:
            unique_tokens.append(token)
            seen.add(token)

    name = " ".join(unique_tokens)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def fuzzy_group_products(
    product_names,
    threshold=85
):

    canonical_map = {}

    canonical_names = []

    for name in product_names:

        if pd.isna(name):
            continue

        matched = False

        for canon in canonical_names:

            score = fuzz.token_set_ratio(
                name,
                canon
            )

            if score >= threshold:

                canonical_map[name] = canon

                matched = True
                break

        if not matched:

            canonical_map[name] = name

            canonical_names.append(name)

    return canonical_map


# =========================================
# NORMALIZE PRODUCT COLUMN
# =========================================
def normalize_product_column(
    df,
    column="product_name",
    threshold=90
):

    # =====================================
    # basic cleaning
    # =====================================
    df["product_name"] = (
        df[column]
        .apply(clean_product_name)
    )

    # =====================================
    # fuzzy similarity grouping
    # =====================================
    canonical_map = fuzzy_group_products(
        df["product_name"].dropna().unique(),
        threshold=threshold
    )

    # =====================================
    # mapping canonical name
    # =====================================
    df["product_name"] = (
        df["product_name"]
        .map(canonical_map)
    )

    return df

def create_product_table(df, platform):

    product_table = (
        df[["product_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    product_table["product_name"] = (
        product_table["product_name"]
        .apply(clean_product_name)
    )


    product_table["product_id"] = [

        f"{platform[:1].upper()}_{i+1:05d}"

        for i in range(len(product_table))
    ]

    return product_table[[
        "product_id",
        "product_name",
        "product_name"
    ]]


# CREATE TRANSACTION TABLE
# ===============================
def create_transaction_table(df, product_table, platform):

    # mapping product_id
    df = df.merge(
        product_table[
            ["product_id", "product_name"]
        ],
        on="product_name",
        how="left"
    )

    prefix = platform[:1].upper()

    # unique order_id
    unique_orders = (
        df["order_id"]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    order_map = {

        order: f"{prefix}_TRX_{i+1:05d}"

        for i, order in enumerate(unique_orders)
    }

    # mapping transaction_id
    df["transaction_id"] = (
        df["order_id"]
        .map(order_map)
    )

    # drop original column
    df = df.drop(
        columns=["product_name", "order_id"],
        errors="ignore"
    )

    return df



# CLEANING FUNCTION

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



# TRANSFORM 

def transform_data(df, platform):

    platform_lower = platform.lower()

    # =================================================
    # RENAME COLUMNS
    # =================================================
    if platform_lower == "shopee":

        df = df.rename(columns={
            "No. Pesanan": "order_id",
            "Nama Produk": "product_name",
            "SKU Induk": "sku",
            "Harga Awal": "price",
            "Total Diskon": "discount",
            "Jumlah": "quantity",
            "Total Harga Produk": "total_sales",
            "Waktu Pesanan Dibuat": "transaction_date"
        })

    elif platform_lower == "lazada":

        df = df.rename(columns={
            "orderNumber": "order_id",
            "itemName": "product_name",
            "sellerSku": "sku",
            "unitPrice": "price",
            "sellerDiscountTotal": "seller_discount",
            "bundleDiscount": "bundle_discount",
            "paidPrice": "total_sales",
            "createTime": "transaction_date"
        })

    elif platform_lower == "tiktok":

        df = df.rename(columns={
            "Order ID": "order_id",
            "Product Name": "product_name",
            "SKU ID": "sku",
            "SKU Unit Original Price": "price",
            "SKU Seller Discount": "seller_discount",
            "SKU Platform Discount": "platform_discount",
            "Quantity": "quantity",
            "SKU Subtotal After Discount": "total_sales",
            "Created Time": "transaction_date"
        })

    # =================================================
    # PRODUCT CLEANING
    # =================================================
    
    if platform.lower() == "shopee":
        df["price"] = df["price"].apply(clean_shopee)
        df["discount"] = df["discount"].apply(clean_discount)
        df["total_sales"] = df["total_sales"].apply(clean_shopee)
    
    elif platform.lower() == "lazada":

        df["discount"] = (
            df["seller_discount"].fillna(0) +
            df["bundle_discount"].fillna(0)
        ).abs()

        df["quantity"] = 1

        df = (
            df.groupby(
                ["order_id",  "product_name","transaction_date", "sku"],
                as_index=False
            )
            .agg({
                "price": "first",
                "discount": "sum",
                "total_sales": "sum",
                "quantity": "sum"
            })
        )
    
    elif platform.lower() == "tiktok":

        df["discount"] = (
            df["seller_discount"].fillna(0) +
            df["platform_discount"].fillna(0)
        )

    df["product_name"] = df["product_name"].apply(clean_product_name)


    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
    df["total_sales"] = pd.to_numeric(df["total_sales"], errors="coerce")

    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
    df["platform"] = platform.capitalize()

    df["price"] = df.apply(fix_price, axis=1)
    df["discount"] = df.apply(fix_discount, axis=1)

   
   
    df = df[[
        "product_name",
        "price",
        "discount",
        "quantity",
        "total_sales",
        "transaction_date",
        "platform"

    ]]

    return df


# INTEGRATION

def integrate_data(dfs):
    integrate = pd.concat(dfs, ignore_index=True)
    integrate = integrate.sort_values(by="transaction_date", ascending=False)
    
    return integrate


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

