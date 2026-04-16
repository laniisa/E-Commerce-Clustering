import pandas as pd

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
def category_platform(df):
    return (
        df.groupby(['platform', 'product_category'])['total_sales']
        .sum()
        .reset_index()
    )

def category_sales(df):
    return df.groupby("product_category")["total_sales"].sum().sort_values(ascending=False)

# ======================
# TOP PRODUK
# ======================
def top_products(df):
    return (
        df.groupby("product_category")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

def top_revenue(df):
    return (
        df.groupby("product_desc")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

# ======================
# DISTRIBUTION
# ======================
def platform_distribution(df):
    return df["platform"].value_counts()

def discount_effect(df):
    return df[["discount", "total_sales"]]
# ======================
# BEST DAY
# ======================
def sales_per_day(df):
    df["day_name"] = df["transaction_date"].dt.day_name()
    return df.groupby("day_name")["total_sales"].sum()