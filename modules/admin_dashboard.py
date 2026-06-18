import pandas as pd
import streamlit as st
import bcrypt
from config.database import connect_db
from modules.auth import *

def get_users():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT
        id_user,
        username,
        email,
        role,
        created_at
    FROM users
    ORDER BY created_at DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(users)

def get_history():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT
        c.id,
        u.username,
        d.dataset_name,
        c.k_cluster,
        c.method,
        c.silhouette_score,
        c.dbi_score,
        c.file_path_result,
        c.file_path_plot,
        c.created_at
    FROM clustering c
    JOIN users u ON c.user_id = u.id_user
    JOIN datasets d ON c.dataset_id = d.id
    ORDER BY c.created_at DESC;
    """)

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(history)

def get_datasets():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT
        d.id,
        u.username,
        d.dataset_name,
        d.created_at,
        
        COUNT(c.id) AS total_files,

        GROUP_CONCAT(
            CONCAT(c.platform, ': ', c.file_name)
            SEPARATOR ', '
        ) AS file_names
    FROM datasets d
    JOIN users u ON d.user_id = u.id_user
    LEFT JOIN dataset_files c ON c.dataset_id = d.id
    GROUP BY
        d.id,
        u.username,
        d.dataset_name,
        d.created_at
    ORDER BY d.created_at DESC;
    """)

    get_datasets = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(get_datasets)

def get_dataset_files(dataset_id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        id,file_name,platform,file_path,rows_count,cols_count,uploaded_at
    FROM dataset_files
    WHERE dataset_id=%s
    ORDER BY uploaded_at
    """, (dataset_id,))

    files = cursor.fetchall()

    cursor.close()
    conn.close()

    return files

def dashboard_admin():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # total dataset user
    cur.execute("""
        SELECT COUNT(*) AS total_dataset
        FROM datasets
    """)
    total_dataset = cur.fetchone()["total_dataset"]
    
    #total user
    cur.execute("""
        SELECT COUNT(*) AS total_files
        FROM dataset_files
    """)
    total_files = cur.fetchone()["total_files"]

    # summary clustering
    cur.execute("""
        SELECT 
            COUNT(*) AS total_analisis
        FROM clustering
    """)
    total_analisis = cur.fetchone()["total_analisis"]

    cur.close()
    conn.close()

    return {
        "total_dataset": total_dataset or 0,
        "total_files": total_files or 0,
        "total_analisis": total_analisis or 0,
    }

def get_platform_chart():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT
            platform,
            COUNT(*) total
        FROM dataset_files
        GROUP BY platform
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return pd.DataFrame(data)

def add_users(username, email, password, role):
    conn = connect_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        query = """
        INSERT INTO users (username, email, password, role)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, email, hashed, role))
        conn.commit()
        return True

    except Exception as e:
        print("Error:", e)
        return False

    finally:
        conn.close()

def update_user(id_user, username, email, role, password=None):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        if password:
            hashed = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
            query = """
            UPDATE users
            SET username=%s,email=%s,role=%s,password=%s
            WHERE id_user=%s
            """

            cursor.execute(
                query,
                (username, email, role, hashed, id_user)
            )

        else:

            query = """
            UPDATE users
            SET username=%s,email=%s,role=%s
            WHERE id_user=%s
            """

            cursor.execute(
                query,( username,email, role, id_user )
            )

        conn.commit()
        return True
    
    except Exception as e:
        print("Error:", e)
        return False

    finally:
        cursor.close()
        conn.close()

def delete_user(id_user):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM users WHERE id_user=%s",
            (int(id_user),)
        )

        conn.commit()
        return True
    except Exception as e:
        print("Error:", e)
        return False

    finally:
        cursor.close()
        conn.close()


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

def delete_analisis_db(id):
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

@st.dialog("Tambah User")
def add_user():

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")
    role = st.selectbox("Role",["user", "admin"])

    c1,c2 = st.columns(2)
    with c1:
        if st.button(
            "Tambah",
            use_container_width=True
        ):
            if not username or not email or not password:
                st.warning("Semua field wajib diisi!")
            elif not is_valid_email(email):
                st.error("Format email tidak valid!")
            elif password != confirm:
                st.error("Password tidak sama!")
            else:
                valid, msg = is_strong_password(password)
                if not valid:
                    st.error(msg)
                else:

                    if add_users(username,email,password,role):
                        st.success("Berhasil menambahkan pengguna!")
                        st.rerun()
                    else:
                        st.error("Gagal menambah user")
    with c2:
        if st.button("Batal",use_container_width=True):
            st.rerun()


@st.dialog("Edit User")
def edit_user(user_data):

    username = st.text_input( "Username", value=user_data["username"] )
    email = st.text_input("Email", value=user_data["email"])
    new_password = st.text_input("Password Baru",type="password")
    confirm_password = st.text_input("Konfirmasi Password Baru",type="password")
    role = st.selectbox(
        "Role", ["user", "admin"],
        index=0 if user_data["role"]=="user" else 1
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Simpan", use_container_width=True):
            if not is_valid_email(email):
                st.error("Format email tidak valid!")
            elif new_password:

                if new_password != confirm_password:
                    st.error("Password tidak sama!")

                else:
                    valid, msg = is_strong_password(new_password)
                    if not valid:
                        st.error(msg)
                    else:
                        if update_user(user_data["id_user"],username,email,role,new_password):
                            st.success("Pengguna berhasil diupdate")
                            st.rerun()
                        else :
                            st.error("Gagal Mengupdate pengguna")
            else:
                if update_user(user_data["id_user"],username,email,role ):
                    st.success("Pengguna berhasil diupdate")
                    st.rerun()
                else :
                    st.error("Gagal Mengupdate pengguna")  

    with c2:
        if st.button("Batal", use_container_width=True):
            st.rerun()

@st.dialog("Konfirmasi Hapus")
def confirm_delete(user):
    st.warning(f"Yakin ingin menghapus user '{user['username']}'?")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Hapus", use_container_width=True ):
            delete_user(user["id_user"])
            st.success("User berhasil dihapus")
            st.rerun()

    with c2:
        if st.button("Batal",use_container_width=True):
            st.rerun()


@st.dialog("Detail Analisis", width="large")
def detail_analisis(row):
    d1,d2 = st.columns([1,2])
    
    with d1:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**User:** {row['username']}")
            st.write(f"**Dataset:** {row['dataset_name']}")
            st.metric("Silhouette Score",round(row["silhouette_score"], 4))

        with col2:
            st.write(f"**Metode:** {row['method']}")
            st.write(f"**Jumlah Cluster:** {row['k_cluster']}")
            st.metric("DBI Score",round(row["dbi_score"], 4))

        st.write(f"**Tanggal:** {row['created_at']}")

        # Plot clustering
        if row["file_path_plot"]:
            st.image(row["file_path_plot"], use_container_width=True)

    with d2:
        st.subheader("Hasil Analisis")

        if row["file_path_result"]:

            try:
                df_result = pd.read_csv(row["file_path_result"])

                st.dataframe(
                    df_result, use_container_width=True, width=700)

            except:
                st.warning("File hasil tidak ditemukan")

@st.dialog("Konfirmasi Hapus Analisis")
def delete_analisis(history):

    st.warning(
        f"Yakin ingin menghapus analisis '{history['dataset_name']}'?"
    )
    c1, c2 = st.columns(2)

    with c1:

        if st.button("Hapus", use_container_width=True):
            if delete_analisis_db(history["id"]):
                st.success("Analisis berhasil dihapus")
                st.rerun()

            else:
                st.error("Gagal menghapus analisis")

    with c2:
        if st.button("Batal",use_container_width=True):
            st.rerun()


@st.dialog("Detail Datasets", width="large")
def detail_datasets(row):
    st.write(f"**User:** {row['username']}")
    st.write(f"**Dataset:** {row['dataset_name']}")
    st.write(f"**Tanggal:** {row['created_at']}")
    
    st.subheader("File Datasets")

    files = get_dataset_files(row["id"])
    if len(files) == 0:
        st.warning("Tidak ada file dataset")

    for file in files:

        platform = file["platform"]
        filename = file["file_name"]

        with st.expander(f"{platform} • {filename}"):

            c1,c2 = st.columns(2)

            c1.metric( "Rows",file["rows_count"])
            c2.metric("Cols", file["cols_count"])

            try:
                df_result = pd.read_csv(file["file_path"])
                st.dataframe(df_result,use_container_width=True)
            except:
                st.warning("File tidak ditemukan")

@st.dialog("Konfirmasi Hapus Datasets")
def delete_datasets(datasets):

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

            