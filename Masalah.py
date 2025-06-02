import streamlit as st
import pandas as pd
import requests

# 🔗 Ganti ini dengan URL Web App dari Apps Script kamu
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzuls9ToUF3CaJ47bwElktRDC3buHwfFM6vwv7ziWeeWlDDDni6iSvE-dswpW0HwBw7mA/exec"

def run():
    # ============================
    # 1. Tampilkan isi Sheet "Masalah"
    # ============================
    st.subheader("📋 Manajemen Data Sheet 'Masalah'")
    df_masalah = pd.DataFrame()

    try:
        response = requests.get(WEB_APP_URL + "?sheet=Masalah")
        if response.status_code == 200:
            data = response.json()
            df_masalah = pd.DataFrame(data, columns=["Mesin", "Masalah"])
            st.dataframe(df_masalah, use_container_width=True)
        else:
            st.warning(f"Gagal mengambil data Masalah: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error mengambil data Masalah: {e}")

    # ============================
    # 2. Form Tambah Data ke Sheet "Masalah"
    # ============================
    st.subheader("➕ Tambah Masalah Baru")

    mesin_list = []
    try:
        mesin_response = requests.get(WEB_APP_URL + "?sheet=Mesin")
        if mesin_response.status_code == 200:
            mesin_data = mesin_response.json()
            mesin_list = [row[1] for row in mesin_data if len(row) > 1]
        else:
            st.warning("Gagal ambil data dari Sheet Mesin.")
    except Exception as e:
        st.warning(f"⚠️ Error ambil data Mesin: {e}")

    if mesin_list:
        selected_mesin = st.selectbox("Pilih Mesin", mesin_list)
        new_masalah = st.text_input("Masukkan Masalah")

        if st.button("📝 Tambahkan Masalah"):
            if new_masalah.strip():
                new_pair = (selected_mesin.strip().lower(), new_masalah.strip().lower())
                existing_pairs = df_masalah.apply(lambda row: (
                    str(row['Mesin']).strip().lower(),
                    str(row['Masalah']).strip().lower()
                ), axis=1).tolist()

                if new_pair in existing_pairs:
                    st.warning("⚠️ Kombinasi Mesin dan Masalah sudah ada.")
                else:
                    payload = {"mesin": selected_mesin, "masalah": new_masalah.strip()}
                    response = requests.post(WEB_APP_URL + "?func=addMasalah", json=payload)

                    if response.status_code == 200 and "Masalah Added" in response.text:
                        st.success("✅ Masalah berhasil ditambahkan.")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal menambahkan: {response.text}")
            else:
                st.warning("⚠️ Masalah tidak boleh kosong.")

    # ============================
    # 3. Hapus Baris dari Sheet "Masalah"
    # ============================
    st.subheader("❌ Hapus Masalah")

    if not df_masalah.empty:
        label_list = df_masalah.apply(lambda row: f"{row['Mesin']} - {row['Masalah']}", axis=1)
        selected_index = st.selectbox(
            "Pilih baris yang ingin dihapus:",
            df_masalah.index,
            format_func=lambda i: label_list[i]
        )

        if st.button("🗑️ Hapus Masalah"):
            payload = {"index": int(selected_index)}
            delete_response = requests.post(WEB_APP_URL + "?func=deleteMasalah", json=payload)

            if delete_response.status_code == 200 and "Deleted" in delete_response.text:
                st.success("✅ Masalah berhasil dihapus.")
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus: {delete_response.text}")
