import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler


# ======================
# BASIC INFO
# ======================
def get_overview(df):
    return {
        "total_data": len(df),
        "total_category": df["product_category"].nunique(),
        "total_platform": df["platform"].nunique(),
        "min_date": df["transaction_date"].min(),
        "max_date": df["transaction_date"].max()
    }

# ======================
# DESCRIPTIVE
# ======================
def descriptive_stats(df, num_cols):
    return df[num_cols].describe()

# ======================
# CORRELATION
# ======================
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
            total_transaksi=("product_code", "count")
        )
        .reset_index()
    )
# ======================
# TREND
# ======================
def monthly_trend(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    df = df.set_index("transaction_date")

    trend = df.resample("M").agg({
        "total_sales": "sum",
        "quantity": "sum",
        "product_code": "count"
    }).reset_index()

    trend["year_month"] = trend["transaction_date"].dt.strftime("%Y-%m")

    return trend

# ======================
# TREND PER PLATFORM
# ======================
def trend_platform(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    result = (
        df.set_index("transaction_date")
        .groupby("platform")
        .resample("M")
        .sum(numeric_only=True)
        .reset_index()
    )

    result["year_month"] = result["transaction_date"].dt.strftime("%Y-%m")

    return result

# ======================
# CATEGORY
# ======================
def category_sales_platform(df):
    return (
        df.groupby(['platform', 'product_category'])['total_sales']
        .sum()
        .reset_index()
    )

def category_sales(df):
    return (
        df.groupby("product_category")["total_sales"]
        .sum()
        .sort_values(ascending=False)
    )

def category_quantity(df):
    return (
        df.groupby("product_category")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

def category_quantity_platform(df):
    return (
        df.groupby(['platform', 'product_category'])['quantity']
        .sum()
        .reset_index()
    )

def monthly_pattern(df):
    df = df.copy()
    df["month_num"] = pd.to_datetime(df["transaction_date"]).dt.month
    df["month_name"] = pd.to_datetime(df["transaction_date"]).dt.month_name()

    result = (
        df.groupby(["month_num", "month_name"])["total_sales"]
        .mean()
        .reset_index()
        .sort_values("month_num")
    )
    return result

def peak_low_per_year(trend_all):
    trend_all = trend_all.copy()
    trend_all["year"] = pd.to_datetime(trend_all["year_month"]).dt.year
    trend_all["month"] = pd.to_datetime(trend_all["year_month"]).dt.month_name()

    peak = trend_all.loc[
        trend_all.groupby("year")["total_sales"].idxmax()
    ]

    low = trend_all.loc[
        trend_all.groupby("year")["total_sales"].idxmin()
    ]

    return peak, low

def category_monthly(df):
    df = df.copy()
    df["year_month"] = pd.to_datetime(df["transaction_date"]).dt.to_period("M").astype(str)

    result = (
        df.groupby(["year_month", "product_category"])["total_sales"]
        .sum()
        .reset_index()
    )

    return result

def category_monthly_platform(df):
    df = df.copy()
    df["year_month"] = pd.to_datetime(df["transaction_date"]).dt.to_period("M").astype(str)

    result = (
        df.groupby(["year_month", "platform", "product_category"])["total_sales"]
        .sum()
        .reset_index()
    )

    return result
# ======================
# DISTRIBUTION
# ======================
def platform_distribution(df):
    return df["platform"].value_counts()

def discount_effect(df):
    return df[["discount", "total_sales", "platform"]]
# ======================
# BEST DAY
# ======================
def sales_per_day(df):
    df = df.copy()

    df["day_name"] = df["transaction_date"].dt.day_name()

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    result = (
        df.groupby("day_name")["total_sales"]
        .sum()
        .reset_index()
    )

    result["day_name"] = pd.Categorical(
        result["day_name"],
        categories=day_order,
        ordered=True
    )

    result = result.sort_values("day_name")

    return result

def normalize_data(df):
    df = df.copy()

    num_cols = ["price", "discount", "quantity", "total_sales"]

    # log transform (handle skew & outlier ringan)
    X_log = np.log1p(df[num_cols])

    # robust scaler (tahan outlier)
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_log)

    df[num_cols] = X_scaled

    return df