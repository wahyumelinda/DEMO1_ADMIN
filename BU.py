import streamlit as st
import pandas as pd
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbx79d0WrN8wW_Z2clc9EZZySSJHSI_PRb4djgo1s-Houpu9QDvsc6CgKyR-F7tmFWvxPQ/exec"

st.title("📋 Manajemen BU di Google Sheet")

def run():
    st.subheader("📄 Data BU yang Sudah Ada")
    df = pd.DataFrame()

    try:
        response = requests.get(WEB_APP_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=["BU"])
            st.dataframe(df, use_container_width=True)
            st.write("---")
            
            # ============================
            # 1. Tambah Data (DILETAKKAN DI ATAS)
            # ============================
            st.subheader("➕ Tambah BU Baru")
            new_value = st.text_input("Masukkan BU Baru (misal SC3):")

            if st.button("📝 Tambahkan ke Sheet"):
                if new_value.strip() != "":
                    new_value_clean = new_value.strip()
                    if not df["BU"].str.lower().isin([new_value_clean.lower()]).any():
                        payload = {"value": new_value_clean}
                        post_response = requests.post(WEB_APP_URL, json=payload)
                        if post_response.status_code == 200 and post_response.text == "Success":
                            st.success("✅ Data berhasil ditambahkan!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal menambahkan: {post_response.text}")
                    else:
                        st.error("⚠️ Data BU sudah ada. Tidak boleh duplikat.")
                else:
                    st.warning("⚠️ Input tidak boleh kosong.")
            st.write("---")
            
            # ============================
            # 2. Hapus Data (DILETAKKAN DI BAWAH)
            # ============================
            st.subheader("❌ Hapus BU")
            if not df.empty:
                selected_index = st.selectbox(
                    "Pilih data yang ingin dihapus:",
                    df.index,
                    format_func=lambda i: df.loc[i, "BU"]
                )
                if st.button("🗑️ Hapus"):
                    delete_payload = {"index": int(selected_index)}
                    delete_response = requests.post(
                        WEB_APP_URL + "?func=delete",
                        json=delete_payload
                    )
                    if delete_response.status_code == 200 and delete_response.text == "Deleted":
                        st.success("✅ Data berhasil dihapus!")
                        st.rerun()
                    else:
                        st.error(f"❌ Gagal menghapus: {delete_response.text}")

        else:
            st.error("❌ Gagal mengambil data dari Google Sheet.")

    except Exception as e:
        st.error(f"❌ Error saat mengambil data: {e}")
