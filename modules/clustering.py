import pandas as pd
import numpy as np
from config.database import connect_db
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
from pathlib import Path
import datetime
import warnings

# =========================
# PREPARE DATA
# =========================
def prepare_clustering_data(df):
    features = ["price", "discount", "quantity", "total_sales"]

    X = df[features].copy()
    
    if X.isnull().any().any():
        X = X.fillna(X.mean())
        warnings.warn("Missing values detected and filled with column means")
    
    return X

# ===============================
# SILHOUETTE SCORE
# ===============================
def calculate_silhouette_scores(X, k_range=range(2, 11)):
    """Calculate silhouette scores for different k values"""
    scores = {}
    
    for k in k_range:
        if k >= X.shape[0]:
            continue
            
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kmedoids = KMedoids(
                n_clusters=k,
                metric="euclidean",
                init="k-medoids++",
                method="alternate",
                random_state=42,
                max_iter=300
            )
            labels = kmedoids.fit_predict(X)
        
        # Check if we have at least 2 unique clusters
        unique_labels = len(np.unique(labels))
        if unique_labels < 2:
            scores[k] = -1
            continue
            
        try:
            score = silhouette_score(X, labels, metric="euclidean")
            scores[k] = score
        except Exception as e:
            scores[k] = -1
            print(f"Error for k={k}: {e}")
    
    return scores

# =========================
# FIND BEST K (SILHOUETTE)
# =========================
def find_best_k(X, k_range=range(2, 11)):
    best_k = 2
    best_score = -1
    scores = {}

    for k in k_range:
        if k >= X.shape[0]:
            continue
        try:
            model = KMedoids(
                n_clusters=k,
                init="k-medoids++", 
                metric="euclidean", 
                method="alternate",
                random_state=42
            )
            labels = model.fit_predict(X)

            # 🔥 cek jumlah cluster unik
            if len(np.unique(labels)) < 2:
                scores[k] = -1
                continue

            score = silhouette_score(X, labels, metric="euclidean")
            scores[k] = score

            if score > best_score:
                best_score = score
                best_k = k

        except Exception as e:
            scores[k] = -1

    return best_k, scores

# =========================
# CLUSTERING
# =========================
def run_kmedoids(X, k):
    model = KMedoids(
        n_clusters=k,
        init="k-medoids++", 
        metric="euclidean",
        method="alternate",  
        random_state=42,
        max_iter=300
    )
    labels = model.fit_predict(X)
    return labels, model

def attach_cluster(df, labels):
    df = df.copy()
    df["cluster"] = labels
    return df

# =========================
# EVALUATION
# =========================
def evaluate_clustering(X, labels):
    return {
        "DBI": davies_bouldin_score(X, labels),
        "Silhouette": silhouette_score(X, labels)
    }

# =========================
# SAVE CSV
# =========================
def save_cluster_csv(df, dataset_id):
    folder = Path(f"assets/clustering/dataset_{dataset_id}")
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"cluster_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = folder / filename

    df.to_csv(path, index=False)

    return str(path)

# =========================
# SAVE PLOT
# =========================
def save_plot(df, dataset_id):
    folder = Path(f"assets/clustering/dataset_{dataset_id}")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "cluster_plot.png"

    plt.figure()
    plt.scatter(df["price"], df["total_sales"], c=df["cluster"])
    plt.xlabel("Price")
    plt.ylabel("Total Sales")
    plt.title("Cluster Visualization")
    plt.savefig(path)
    plt.close()

    return str(path)

def save_summary(dataset_id, user_id, k, method, silhouette, dbi, file_csv, file_plot):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO clustering_summary
    (dataset_id, user_id, k_cluster, method, silhouette_score, dbi_score, file_path_result, file_path_plot)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        dataset_id, user_id, k, method,
        silhouette, dbi,
        file_csv, file_plot
    ))

    conn.commit()
    cursor.close()
    conn.close()

# =========================
# SUMMARY PER CLUSTER
# =========================
def get_cluster_summary(df):
    summary = df.groupby("cluster").agg({
        "price": "mean",
        "discount": "mean",
        "quantity": "mean",
        "total_sales": "mean",
        "cluster": "count"
    }).rename(columns={"cluster": "total_data"})

    return summary.reset_index()


# =========================
# LABEL CLUSTER
# =========================
def label_cluster(summary):
    sorted_clusters = summary.sort_values("total_sales")

    labels = {}

    for i, row in enumerate(sorted_clusters.itertuples()):
        if i == 0:
            labels[row.cluster] = "Low Value"
        elif i == len(sorted_clusters) - 1:
            labels[row.cluster] = "High Value"
        else:
            labels[row.cluster] = "Medium Value"

    return labels


# =========================
# GENERATE INSIGHT TEXT
# =========================
def generate_insight(summary, labels):
    insights = []

    for row in summary.itertuples():
        label = labels[row.cluster]

        insight = f"""
        Cluster {row.cluster} ({label}):
        - Rata-rata harga: {round(row.price,2)}
        - Rata-rata quantity: {round(row.quantity,2)}
        - Rata-rata total sales: {round(row.total_sales,2)}
        """

        if label == "High Value":
            insight += "👉 Produk sangat potensial (high sales)"
        elif label == "Low Value":
            insight += "👉 Perlu strategi peningkatan penjualan"
        else:
            insight += "👉 Performa sedang"

        insights.append(insight)

    return insights