import streamlit as st
import pandas as pd
import requests

# 🔗 Ganti ini dengan URL Web App dari Apps Script kamu
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzyJfNTlKVzzaLZQhSNcnx-yrpqy3NO1h9uw4w9-oPj7OXBY8xeh73MPxlaOqFl3AlR/exec"

def run() :
    # ============================
    # 1. Tampilkan isi Sheet "PIC"
    # ============================
    st.subheader("📋 Manajemen Data Sheet 'PIC'")
    df_pic = pd.DataFrame()

    try:
        pic_response = requests.get(WEB_APP_URL + "?sheet=PIC")
        if pic_response.status_code == 200:
            pic_data = pic_response.json()
            df_pic = pd.DataFrame(pic_data, columns=["BU", "PIC"])
            st.dataframe(df_pic, use_container_width=True)
        else:
            st.warning(f"Gagal mengambil data PIC: {pic_response.status_code}")
    except Exception as e:
        st.error(f"❌ Error mengambil data PIC: {e}")

    st.write("---")
    
    # ============================
    # 2. Form Tambah Data ke PIC
    # ============================
    st.subheader("➕ Tambah PIC Baru")

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
        new_pic = st.text_input("Masukkan Nama PIC")

    if st.button("📝 Tambahkan ke Sheet PIC"):
        if new_pic.strip():
            # Validasi duplikat: cek apakah SC-PIC sudah ada
            new_pair = (selected_sc.strip().lower(), new_pic.strip().lower())
            existing_pairs = df_pic.apply(lambda row: (str(row['BU']).strip().lower(), str(row['PIC']).strip().lower()), axis=1).tolist()

            if new_pair in existing_pairs:
                st.warning("⚠️ Kombinasi BU dan PIC ini sudah ada. Duplikat tidak diizinkan.")
            else:
                payload = {"sc": selected_sc, "pic": new_pic.strip()}
                response = requests.post(WEB_APP_URL + "?func=addPIC", json=payload)

                if response.status_code == 200 and "PIC Added" in response.text:
                    st.success("✅ Baris berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal menambahkan: {response.text}")
        else:
            st.warning("⚠️ Nama PIC tidak boleh kosong.")

    st.write("---")
    
    # ============================
    # 3. Hapus Baris dari PIC
    # ============================
    st.subheader("❌ Hapus PIC")

    if not df_pic.empty:
        label_list = df_pic.apply(lambda row: f"{row['BU']} - {row['PIC']}", axis=1)
        selected_index = st.selectbox(
            "Pilih baris yang ingin dihapus:",
            df_pic.index,
            format_func=lambda i: label_list[i]
        )

        if st.button("🗑️ Hapus Baris"):
            payload = {"index": int(selected_index)}
            delete_response = requests.post(WEB_APP_URL + "?func=deletePIC", json=payload)

            if delete_response.status_code == 200 and "Deleted" in delete_response.text:
                st.success("✅ Baris berhasil dihapus.")
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus: {delete_response.text}")
