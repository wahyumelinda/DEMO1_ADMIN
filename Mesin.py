import streamlit as st
import pandas as pd
import requests

# 🔗 Ganti ini dengan URL Web App dari Apps Script kamu
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwyMwcajv9eIhEeA8Zxy3t7JHPuS2vMTdcmn85WE5pVu6zlSdHVLK1e7XFpLykSpSTL/exec"

def run():
    # ============================
    # 1. Tampilkan isi Sheet "Mesin"
    # ============================
    st.subheader("📋 Manajemen Data Sheet 'Mesin'")
    df_mesin = pd.DataFrame()

    try:
        mesin_response = requests.get(WEB_APP_URL + "?sheet=Mesin")
        if mesin_response.status_code == 200:
            mesin_data = mesin_response.json()
            df_mesin = pd.DataFrame(mesin_data, columns=["BU", "Mesin"])
            st.dataframe(df_mesin, use_container_width=True)
        else:
            st.warning(f"Gagal mengambil data Mesin: {mesin_response.status_code}")
    except Exception as e:
        st.error(f"❌ Error mengambil data Mesin: {e}")
        
    st.write("---")
    # ============================
    # 2. Form Tambah Data ke Mesin
    # ============================
    st.subheader("➕ Tambah Mesin Baru")

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
        new_mesin = st.text_input("Masukkan Nama Mesin")

    if st.button("📝 Tambahkan ke Sheet Mesin"):
        if new_mesin.strip():
            # Validasi duplikat: cek apakah SC-Mesin sudah ada
            new_pair = (selected_sc.strip().lower(), new_mesin.strip().lower())
            existing_pairs = df_mesin.apply(lambda row: (str(row['BU']).strip().lower(), str(row['Mesin']).strip().lower()), axis=1).tolist()

            if new_pair in existing_pairs:
                st.warning("⚠️ Kombinasi BU dan Mesin ini sudah ada. Duplikat tidak diizinkan.")
            else:
                payload = {"sc": selected_sc, "mesin": new_mesin.strip()}
                response = requests.post(WEB_APP_URL + "?func=addMesin", json=payload)

                if response.status_code == 200 and "Mesin Added" in response.text:
                    st.success("✅ Baris berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal menambahkan: {response.text}")
        else:
            st.warning("⚠️ Nama Mesin tidak boleh kosong.")

    st.write("---")
    # ============================
    # 3. Hapus Baris dari Mesin
    # ============================
    st.subheader("❌ Hapus Mesin")

    if not df_mesin.empty:
        label_list = df_mesin.apply(lambda row: f"{row['BU']} - {row['Mesin']}", axis=1)
        selected_index = st.selectbox(
            "Pilih baris yang ingin dihapus:",
            df_mesin.index,
            format_func=lambda i: label_list[i]
        )

        if st.button("🗑️ Hapus Baris"):
            payload = {"index": int(selected_index)}
            delete_response = requests.post(WEB_APP_URL + "?func=deleteMesin", json=payload)

            if delete_response.status_code == 200 and "Deleted" in delete_response.text:
                st.success("✅ Baris berhasil dihapus.")
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus: {delete_response.text}")
