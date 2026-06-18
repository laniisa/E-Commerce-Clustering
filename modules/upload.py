import os
import pandas as pd
import uuid
import streamlit as st
from config.database import connect_db

UPLOAD_FOLDER = "assets/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def detect_platform(filename):
    filename = filename.lower()

    if "shopee" in filename:
        return "Shopee"
    elif "lazada" in filename:
        return "Lazada"
    elif "tiktok" in filename:
        return "TikTok"
    else:
        return "Unknown"
    
def save_dataset(user_id, dataset_name, files):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # insert dataset
        cursor.execute(
            "INSERT INTO datasets (user_id, dataset_name) VALUES (%s, %s)",
            (user_id, dataset_name)
        )
        dataset_id = cursor.lastrowid

        saved_files = []

        for file in files:
            try:

                platform = detect_platform(file.name)
                if platform == "Unknown" :
                    continue

                base_name = os.path.splitext(file.name)[0]
                csv_filename = f"{base_name}.csv"
                unique_name = f"{uuid.uuid4()}_{csv_filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_name)

                # read file
                if file.name.lower().endswith(".csv"):
                    df = pd.read_csv(file)
                elif file.name.lower().endswith(".xlsx"):
                    df = pd.read_excel(file, engine='openpyxl')
                else:
                    continue
                
                df.to_csv(filepath, index=False)
                rows, cols = df.shape

                cursor.execute("""
                    INSERT INTO dataset_files 
                    (dataset_id, file_name, file_path, platform, rows_count, cols_count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (dataset_id, csv_filename, filepath, platform, rows, cols))

                saved_files.append(file.name)

            except Exception as e:
                print(f"Error file {file.name}: {e}")
                continue    

        conn.commit()
        return True, dataset_id

    except Exception as e:
        return False, str(e)

    finally:
        cursor.close()
        conn.close()


# ======================
# GET DATASET HISTORY
# ======================
def get_datasets(user_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.id, d.dataset_name, COUNT(f.id) as total_files
        FROM datasets d
        LEFT JOIN dataset_files f ON d.id = f.dataset_id
        WHERE d.user_id = %s
        GROUP BY d.id
        ORDER BY d.created_at DESC
    """, (user_id,))

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_dataset_files(dataset_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM dataset_files WHERE dataset_id=%s",
        (dataset_id,)
    )

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_dataset_by_id(dataset_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM datasets WHERE id=%s",
        (dataset_id,)
    )

    data = cursor.fetchone()

    cursor.close()
    conn.close()
    return data

def show_upload_summary(df, file_name, platform):
    colors = {
        "shopee": "#f97316",
        "lazada": "#3b82f6",
        "tiktok": "#111827"
    }

    color = colors.get(platform.lower(), "#64748b")

    st.markdown(f"""
    <div class="summary-box">
        <div><b>{file_name}</b></div>
        <div class="summary-meta">
            Platform: <span style="color:{color}; font-weight:600;">{platform.capitalize()}</span> |
            Rows: {df.shape[0]} |
            Columns: {df.shape[1]}
        </div>
    </div>
    """, unsafe_allow_html=True)

def delete_datasets_db(id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM datasets WHERE id=%s",
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

@st.dialog("Konfirmasi Hapus Datasets")
def delete_upload(datasets):

    st.warning(
        f"Yakin ingin menghapus datasets '{datasets['dataset_name']}'?"
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Hapus", use_container_width=True):
            if delete_datasets_db(datasets["id"]):
                st.success("Datasets berhasil dihapus!")
                st.rerun()
            else:
                st.error("Gagal menghapus datasets")

    with c2:
        if st.button(
            "Batal",
            use_container_width=True
        ):
            st.rerun()

            