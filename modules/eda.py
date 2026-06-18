import pandas as pd
import numpy as np


def get_overview(df):
    return {
        "total_data": len(df),
        "total_product": df["product_name"].nunique(),
        "total_platform": df["platform"].nunique(),
        "min_date": df["transaction_date"].min(),
        "max_date": df["transaction_date"].max()
    }

def descriptive_stats(df, num_cols):
    return df[num_cols].describe()

def correlation_matrix(df, num_cols):
    return df[num_cols].corr()

def corr_per_platform(df, num_cols):
    result = {}
    for p in df["platform"].unique():
        result[p] = df[df["platform"] == p][num_cols].corr()
    return result

def platform_contribution(df):
    return (
        df.groupby("platform")
        .agg(
            total_sales=("total_sales", "sum"),
            total_transaksi=("product_name", "count")
        )
        .reset_index()
    )

#TREND PENJUALAN
def monthly_trend(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])


    trend = (df.set_index("transaction_date")
        .resample("ME")
        .agg({
            "total_sales": "sum",
            "quantity": "sum",
            "discount": "mean"
        }).reset_index()
    )
    trend["year_month"] = trend["transaction_date"].dt.strftime("%Y-%m")

    return trend

def trend_platform(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    result = (
        df.set_index("transaction_date")
        .groupby("platform")
        .resample("ME")
        .agg({
            "total_sales": "sum",
            "quantity": "sum",
            "discount": "mean"
        })
        .reset_index()
    )

    result["year_month"] = result["transaction_date"].dt.strftime("%Y-%m")

    return result


# =========================================
# product
# =========================================

# TOP SALES
def product_sales(df, top_n=10):
    result = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return result


# BOTTOM SALES
def product_sales_bottom(df, bottom_n=10):
    result = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=True)
        .head(bottom_n)
        .reset_index()
    )
    return result


# TOP QUANTITY
def product_quantity(df, top_n=10):
    result = (
        df.groupby("product_name")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    return result


# BOTTOM QUANTITY
def product_quantity_bottom(df, bottom_n=10):
    result = (
        df.groupby("product_name")["quantity"]
        .sum()
        .sort_values(ascending=True)
        .head(bottom_n)
        .reset_index()
    )
    return result


# product SALES PLATFORM
def product_sales_platform(df, top_n=10):

    top_product = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    result = (
        df[df["product_name"].isin(top_product)]
        .groupby(['platform', 'product_name'])['total_sales']
        .sum()
        .reset_index()
    )

    return result


# product QUANTITY PLATFORM
def product_quantity_platform(df, top_n=10):

    top_product = (
        df.groupby("product_name")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    result = (
        df[df["product_name"].isin(top_product)]
        .groupby(['platform', 'product_name'])['quantity']
        .sum()
        .reset_index()
    )

    return result


# product MONTHLY
def product_monthly(df, top_n=5):

    df = df.copy()

    df["year_month"] = (
        pd.to_datetime(df["transaction_date"])
        .dt.to_period("M")
        .astype(str)
    )

    top_product = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    result = (
        df[df["product_name"].isin(top_product)]
        .groupby(["year_month", "product_name"])["total_sales"]
        .sum()
        .reset_index()
    )

    return result


# product MONTHLY PLATFORM
def product_monthly_platform(df, top_n=5):

    df = df.copy()

    df["year_month"] = (
        pd.to_datetime(df["transaction_date"])
        .dt.to_period("M")
        .astype(str)
    )

    top_product = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    result = (
        df[df["product_name"].isin(top_product)]
        .groupby(["year_month", "platform", "product_name"])["total_sales"]
        .sum()
        .reset_index()
    )

    return result

# DISKON



def discount_efc(df):
    return df[["discount", "total_sales"]].dropna()

def discount_effect(df):
    return df[["discount", "total_sales", "platform"]].dropna()


# DIAGNOSA DATA

def get_skew_outlier(df, num_cols):
    hasil = []

    for col in num_cols:
        skew = round(df[col].skew(), 3)

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]

        hasil.append({
            "Feature": col,
            "Skewness": skew,
            "Jumlah Outlier": len(outliers),
            "Persentase (%)": round(len(outliers)/len(df)*100,2)
        })

    return pd.DataFrame(hasil)

# DIAGNOSA OTOMATIS DATA

def generate_data_diagnosis(df, num_cols):
    cek = get_skew_outlier(df, num_cols)

    avg_skew = round(cek["Skewness"].mean(), 3)
    avg_out = round(cek["Persentase (%)"].mean(), 2)

    # rule interpretasi skewness
    if avg_skew > 1:
        kondisi = f"Rata-rata skewness data sebesar {avg_skew} menunjukkan distribusi data numerik cenderung highly right-skewed dengan rata-rata outlier {avg_out}%."
        rekom = "Log"

    elif avg_skew > 0.5:
        kondisi = f"Rata-rata skewness data sebesar {avg_skew} menunjukkan distribusi data cukup menceng ke kanan dengan rata-rata outlier {avg_out}%."
        rekom = "Log"

    elif avg_out > 3:
        kondisi = f"Distribusi data relatif cukup stabil namun masih ditemukan rata-rata outlier sebesar {avg_out}%."
        rekom = "Log"

    else:
        kondisi = f"Distribusi data numerik relatif stabil dengan rata-rata skewness {avg_skew} dan outlier {avg_out}%."
        rekom = "None"

    return kondisi, cek, rekom

def log_transform(df):
    df = df.copy()
    num_cols = ["price", "discount", "quantity", "total_sales"]
    df[num_cols] = np.log1p(df[num_cols])
    return df