import streamlit as st
import pandas as pd
import requests

# 🔗 Ganti ini dengan URL Web App dari Apps Script kamu
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxfM7TAIgHXrkPWC3-RguuOdaR-ZGko5woddtYxWFsxEPQXH4EH4x34rlT3YEbKfhCn/exec"

def run():
    # ============================
    # 1. Tampilkan isi Sheet "Produk"
    # ============================
    st.subheader("📋 Manajemen Data Sheet 'Produk'")
    df_produk = pd.DataFrame()

    try:
        produk_response = requests.get(WEB_APP_URL + "?sheet=Produk")
        if produk_response.status_code == 200:
            produk_data = produk_response.json()
            df_produk = pd.DataFrame(produk_data, columns=["BU", "Produk"])
            st.dataframe(df_produk, use_container_width=True)
        else:
            st.warning(f"Gagal mengambil data Produk: {produk_response.status_code}")
    except Exception as e:
        st.error(f"❌ Error mengambil data Produk: {e}")
    
    st.write("---")
    
    # ============================
    # 2. Form Tambah Data ke Produk
    # ============================
    st.subheader("➕ Tambah Produk Baru")

    # Ambil dropdown SC dari sheet BU
    sc_list = []
    try:
        bu_response = requests.get(WEB_APP_URL + "?sheet=BU")
        if bu_response.status_code == 200:
            sc_list = bu_response.json()
        else:
            st.warning("Gagal ambil data dari Sheet BU.")
    except Exception as e:
        st.warning(f"⚠️ Error ambil data BU: {e}")

    if sc_list:
        selected_sc = st.selectbox("Pilih BU", sc_list)
        new_produk = st.text_input("Masukkan Nama Produk")

    if st.button("📝 Tambahkan ke Sheet Produk"):
        if new_produk.strip():
            # Validasi duplikat: cek apakah SC-Produk sudah ada
            new_pair = (selected_sc.strip().lower(), new_produk.strip().lower())
            existing_pairs = df_produk.apply(lambda row: (str(row['BU']).strip().lower(), str(row['Produk']).strip().lower()), axis=1).tolist()

            if new_pair in existing_pairs:
                st.warning("⚠️ Kombinasi BU dan Produk ini sudah ada. Duplikat tidak diizinkan.")
            else:
                payload = {"sc": selected_sc, "produk": new_produk.strip()}
                response = requests.post(WEB_APP_URL + "?func=addProduk", json=payload)

                if response.status_code == 200 and "Produk Added" in response.text:
                    st.success("✅ Baris berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal menambahkan: {response.text}")
        else:
            st.warning("⚠️ Nama Produk tidak boleh kosong.")

    st.write("---")
    
    # ============================
    # 3. Hapus Baris dari Produk
    # ============================
    st.subheader("❌ Hapus Produk")

    if not df_produk.empty:
        label_list = df_produk.apply(lambda row: f"{row['BU']} - {row['Produk']}", axis=1)
        selected_index = st.selectbox(
            "Pilih baris yang ingin dihapus:",
            df_produk.index,
            format_func=lambda i: label_list[i]
        )

        if st.button("🗑️ Hapus Baris"):
            payload = {"index": int(selected_index)}
            delete_response = requests.post(WEB_APP_URL + "?func=deleteProduk", json=payload)

            if delete_response.status_code == 200 and "Deleted" in delete_response.text:
                st.success("✅ Baris berhasil dihapus.")
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus: {delete_response.text}")
