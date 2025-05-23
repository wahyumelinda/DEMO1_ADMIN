import streamlit as st
import pymysql
import hashlib
import base64
import os

def run ():
    # Fungsi koneksi database
    def get_connection():
        return pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"],
            ssl={'ssl': {}},
            cursorclass=pymysql.cursors.DictCursor
        )

    # Fungsi hashing password
    def hash_password(password):
        salt = os.urandom(16)
        salted_password = password.encode() + salt
        hashed_password = hashlib.sha256(salted_password).hexdigest()
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        return hashed_password, salt_b64

    # Fungsi untuk registrasi user baru
    def register_user(username, password, role):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    if existing_user['role'] == role:
                        st.warning("⚠️ Username sudah digunakan. Silakan pilih username lain.")
                    else:
                        st.warning("⚠️ Username sudah terdaftar dengan role berbeda.")
                    return

                hashed_password, salt = hash_password(password)
                cursor.execute("INSERT INTO users (username, password, role, salt) VALUES (%s, %s, %s, %s)",
                            (username, hashed_password, role, salt))
            conn.commit()
            conn.close()
            st.success("✅ Registrasi berhasil!")
        except Exception as e:
            st.error(f"❌ Error registering user: {e}")

    # Fungsi untuk mengambil semua user
    def get_all_users():
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, username, role FROM users ORDER BY id DESC")
                users = cursor.fetchall()
            conn.close()
            return users
        except Exception as e:
            st.error(f"❌ Error fetching users: {e}")
            return []

    # Fungsi untuk menghapus user
    def delete_user(user_id):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()
            st.success("✅ User berhasil dihapus.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error deleting user: {e}")


    # Form Registrasi
    st.subheader("📝 Registrasi User Baru")
    with st.form("register_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        role = st.selectbox("🎭 Pilih Role", ["Supervisor", "Section Manager"])
        submit_register = st.form_submit_button("✅ Register")

    if submit_register:
        if username and password:
            register_user(username, password, role)
        else:
            st.warning("⚠️ Mohon lengkapi semua field.")

    st.markdown("---")

    # Tabel User & Hapus
    st.subheader("🗂️ Daftar User yang Terdaftar")
    users = get_all_users()

    if users:
        for user in users:
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            with col1:
                st.write(f"👤 **{user['username']}**")
            with col2:
                st.write(f"🎭 {user['role']}")
            with col3:
                if st.button("🗑️ Hapus", key=f"hapus_{user['id']}"):
                    delete_user(user['id'])
    else:
        st.info("Belum ada user terdaftar.")
