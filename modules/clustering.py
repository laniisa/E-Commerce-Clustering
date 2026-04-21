import pandas as pd
import numpy as np
import streamlit as st
from config.database import connect_db
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from pathlib import Path
import datetime
import warnings

# =========================
# PREPARE DATA
# =========================
features = ["price", "discount", "quantity", "total_sales"]

def cols_cluster(df):
    X = df.copy()
    
    if X.isnull().any().any():
        X = X.fillna(X.mean())
        warnings.warn("Missing values detected and filled with column means")
    
    return X

# ===============================
# SILHOUETTE SCORE
# ===============================
def silhouette_scores(X, k_range=range(2, 9)):
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

            if len(np.unique(labels)) < 2:
                scores[k] = None
                continue

            score = silhouette_score(X, labels)
            scores[k] = score

        except:
            scores[k] = None

    valid_scores = {k: v for k, v in scores.items() if v is not None}
    best_k = max(valid_scores, key=valid_scores.get) if valid_scores else None

    return best_k, scores

# =========================
# CLUSTERING
# =========================
def run_kmedoids(X, best_k):
    model = KMedoids(
        n_clusters=int(best_k),
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
    unique_labels = len(np.unique(labels))

    if unique_labels < 2:
        return {"DBI": None,"Silhouette": None
        }
    
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
def cluster_plot(df, dataset_id, X):
    folder = Path(f"assets/clustering/dataset_{dataset_id}")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "cluster_plot.png"

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    plt.figure()
    plt.scatter(X_pca[:,0], X_pca[:,1], c=df["cluster"])
    plt.title("Cluster Visualization (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.savefig(path)
    plt.close()

    return str(path)

def save_summary(dataset_id, user_id, k_used, method, silhouette, dbi, file_csv, file_plot):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO clustering_summary
    (dataset_id, user_id, k_cluster, method, silhouette_score, dbi_score, file_path_result, file_path_plot)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        dataset_id, user_id, k_used, method,
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
    }).rename(columns={"cluster": "total_data"}).reset_index()

    return summary
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
            insight += "\n👉 Produk sangat potensial (high sales)"
        elif label == "Low Value":
            insight += "\n👉 Perlu strategi peningkatan penjualan"
        else:
            insight += "\n👉 Performa sedang"

        insights.append(insight)

    return insights