import pandas as pd
import streamlit as st
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
    FROM clustering cs
    JOIN datasets d ON cs.dataset_id = d.id
    WHERE cs.user_id = %s
    ORDER BY cs.created_at DESC
    """

    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()

    return df


def get_dashboard_summary(user_id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # total dataset user
    cur.execute("""
        SELECT COUNT(*) AS total_dataset
        FROM datasets
        WHERE user_id = %s
    """, (user_id,))
    total_dataset = cur.fetchone()["total_dataset"]

    # summary clustering
    cur.execute("""
        SELECT 
            COUNT(*) AS total_analisis,
            AVG(silhouette_score) AS avg_silhouette,
            MIN(dbi_score) AS best_dbi
        FROM clustering
        WHERE user_id = %s
    """, (user_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_dataset": total_dataset or 0,
        "total_analisis": result["total_analisis"] or 0,
        "avg_silhouette": round(result["avg_silhouette"] or 0, 3),
        "best_dbi": round(result["best_dbi"] or 0, 3)
    }

def del_his_analisis(id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM clustering
            WHERE id = %s
            """,
            (int(id),)
        )

        conn.commit()
        return True

    except Exception as e:
        print("Error:", e)
        return False

    finally:
        cursor.close()
        conn.close()

@st.dialog("Konfirmasi Hapus Analisis")
def del_analisis(history):

    st.warning(
        f"Yakin ingin menghapus analisis '{history.dataset_name}'?"
    )
    c1, c2 = st.columns(2)

    with c1:

        if st.button("Hapus", use_container_width=True):
            if del_his_analisis(history.id):
                st.session_state.show_cluster_data = False
                st.success("Analisis berhasil dihapus")
                st.rerun()

            else:
                st.error("Gagal menghapus analisis")

    with c2:
        if st.button("Batal",use_container_width=True):
            st.rerun()

