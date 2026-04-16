import re
import bcrypt
from config.database import connect_db

# ======================
# VALIDASI PASSWORD
# ======================
def is_strong_password(password):
    if len(password) < 8:
        return False, "Minimal 8 karakter"
    if not re.search(r"[A-Z]", password):
        return False, "Harus ada huruf besar"
    if not re.search(r"[a-z]", password):
        return False, "Harus ada huruf kecil"
    if not re.search(r"[0-9]", password):
        return False, "Harus ada angka"
    return True, ""


# ======================
# REGISTER
# ======================
def register_user(username, email, password):
    conn = connect_db()
    cursor = conn.cursor()

    # hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, email, hashed))
        conn.commit()
        return True

    except Exception as e:
        print("Error:", e)
        return False

    finally:
        conn.close()


# ======================
# LOGIN
# ======================
def login_user(email, password):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        print("USER:",user)

        if not user:
            return None
        
        if "password" not in user:
            print("Kolom password tidak ditemukan!")
            return None

        if not user["password"]:
            print("Password kosong di DB!")
            return None

        # cek password hash
        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            return user

        return None

    except Exception as e:
        print("Error:", e)
        return None

    finally:
        conn.close()