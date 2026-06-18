import pandas as pd
import numpy as np
import streamlit as st
from config.database import connect_db
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from pathlib import Path
import warnings
import plotly.express as px


# PREPARE DATA

features = ["price", "discount", "quantity", "total_sales"]

def cols_cluster(df_ready):
    X = df_ready.copy()
    
    if X.isnull().any().any():
        X = X.fillna(X.mean())
        warnings.warn("Missing values detected and filled with column means")
    
    return X


# SILHOUETTE SCORE

def silhouette_scores(X, k_range=range(2, 9)):
    silhouette_list = []
    k_list = []

    for k in k_range:
        try:
            kmedoids = KMedoids(
                n_clusters=k,
                init="k-medoids++",
                metric="euclidean",
                method="alternate",
                random_state=42
            )

            labels = kmedoids.fit_predict(X)

            if len(np.unique(labels)) < 2:
                continue

            silhouette_list.append(silhouette_score(X, labels))
            k_list.append(k)

        except:
            continue

    if len(silhouette_list) == 0:
        return None, {}

    best_k = k_list[np.argmax(silhouette_list)]

    scores = {k: s for k, s in zip(k_list, silhouette_list)}

    return best_k, scores


# CLUSTERING

def run_kmedoids(X, best_k):
    kmedoids_final = KMedoids(
        n_clusters=int(best_k),
        init="k-medoids++", 
        metric="euclidean",
        method="alternate",  
        random_state=42,
        max_iter=300
    )
    labels = kmedoids_final.fit_predict(X)

    return labels, kmedoids_final

def attach_cluster(df_original, labels):
    df_original = df_original.copy()
    df_original["cluster"] = labels
    return df_original


# EVALUATION

def evaluate_clustering(X, labels):
    unique_labels = len(np.unique(labels))

    if unique_labels < 2:
        return {"DBI": None,"Silhouette": None
        }
    
    return {
        "DBI": davies_bouldin_score(X, labels),
        "Silhouette": silhouette_score(X, labels)
    }


# SAVE CSV

def save_cluster_csv(df, dataset_id):
    folder = Path(f"assets/clustering/dataset_{dataset_id}")
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"cluster_{dataset_id}.csv"
    path = folder / filename

    df.to_csv(path, index=False)
    return str(path)

def create_cluster_plot(df, X, dataset_id=None, save=False):

    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # dataframe PCA
    pca_df = pd.DataFrame({
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
        "cluster": df["cluster"].astype(str)
    })

    # plot
    fig = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="cluster",
        title="Cluster Visualization (PCA)",
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    fig.update_traces(marker=dict(size=5))

    # save image
    if save and dataset_id is not None:
        folder = Path(f"assets/clustering/dataset_{dataset_id}")
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / f"cluster_plot_{dataset_id}.png"

        fig.write_image(str(path))

        return fig, str(path)

    return fig



def save_summary(dataset_id, user_id, k_used, method, silhouette, dbi, file_csv, file_plot):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO clustering
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

# SUMMARY PER CLUSTER

def get_cluster_summary(df, cols):
    summary = (
        df.groupby("cluster")[cols]
        .mean()
        .round(2)
    )
    summary["total_data"] = df.groupby("cluster").size()
    return summary.reset_index()


# CHARACTERISTIC PER FEATURE

def characteristic_cluster(df, cols):
    return (
        df.groupby("cluster")[cols].mean().reset_index()
    )



# PLATFORM DOMINANCE

def platform_cluster(df):
    return df.groupby(["cluster","platform"]).size().reset_index(name="jumlah")


# product DOMINANCE

def product_cluster(df):
    return df.groupby(["cluster","product_name"]).size().reset_index(name="jumlah")



# ANALISIS DATA OTOMATIS

def analyze_single_data(df, idx, cols):
    row = df.iloc[idx]
    cluster_id = row["cluster"]

    cluster_mean = df.groupby("cluster")[cols].mean().loc[cluster_id]
    global_mean = df[cols].mean()

    text = f"Data ini berada pada Cluster {cluster_id} karena "

    reasons = []

    for f in cols:
        if row[f] > global_mean[f]:
            reasons.append(f"{f} relatif tinggi")
        else:
            reasons.append(f"{f} relatif rendah")

    text += ", ".join(reasons) + " dibandingkan data lain."

    return text



# PAIRPLOT MATRIX DATA

def scatter_matrix_cluster(df, cols):
    return df[cols + ["cluster"]]


# INTERPRETASI EVALUASI

def silhouette_product(score):
    if score >= 0.71:
        return "Strong structure", "Struktur cluster sangat baik, pemisahan antar cluster terlihat jelas."
    elif score >= 0.51:
        return "Reasonable structure", "Struktur cluster cukup baik dan masih layak digunakan."
    elif score >= 0.26:
        return "Weak structure", "Struktur cluster lemah, terdapat tumpang tindih antar cluster."
    else:
        return "No substantial structure", "Cluster tidak terbentuk secara signifikan."


def generate_cluster_evaluation(evals, k_used):
    sil = evals["Silhouette"]
    dbi = evals["DBI"]

    sil_kat, sil_desc = silhouette_product(sil)
    
    teks = f"""
    Berdasarkan jumlah cluster k = <b>{k_used}</b>, diperoleh nilai 
    <b>Silhouette Score sebesar {round(sil,3)}</b> yang termasuk kategori <b>{sil_kat}</b>. 
    {sil_desc}
    Nilai <b>Davies Bouldin Index sebesar {round(dbi,3)}</b> menunjukkan bahwa cluster yang terbentuk 
    memiliki tingkat compactness dan separation yang {'baik' if dbi < 1 else 'cukup'} karena nilai DBI semakin kecil menandakan kualitas cluster semakin optimal.
    """

    return teks