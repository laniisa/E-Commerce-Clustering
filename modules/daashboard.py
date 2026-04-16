import pandas as pd
from config.database import connect_db

def get_clustering_history(user_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        cs.id,
        d.dataset_name,
        cs.dataset_id,
        cs.k_cluster,
        cs.method,
        cs.silhouette_score,
        cs.dbi_score,
        cs.file_path_result,
        cs.file_path_plot,
        cs.created_at
    FROM clustering_summary cs
    JOIN datasets d ON cs.dataset_id = d.id
    WHERE cs.user_id = %s
    ORDER BY cs.created_at DESC
    """

    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()

    return df