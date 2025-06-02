import streamlit as st
import pandas as pd
import requests

WEB_APP_URL = "https://script.google.com/macros/s/AKfycby-5gMYTR7ioN0GuJYWnQj-mpdmSvsmWLLw6w39WlBHHDt_gwh3o20UEJzieNxpyyYhHQ/exec"

def run():
    st.subheader("📋 Manajemen Data Sheet 'SPV'")
    df = pd.DataFrame()
    
    try:
        response = requests.get(WEB_APP_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=["SPV"])
            st.dataframe(df, use_container_width=True)
            st.write("---")
            
            # ============================
            # 1. Tambah Data (DILETAKKAN DI ATAS)
            # ============================
            st.subheader("➕ Tambah SPV Baru")
            new_value = st.text_input("Masukkan SPV Baru")

            if st.button("📝 Tambahkan ke Sheet"):
                if new_value.strip() != "":
                    new_value_clean = new_value.strip()
                    if not df["SPV"].str.lower().isin([new_value_clean.lower()]).any():
                        payload = {"value": new_value_clean}
                        post_response = requests.post(WEB_APP_URL, json=payload)
                        if post_response.status_code == 200 and post_response.text == "Success":
                            st.success("✅ Data berhasil ditambahkan!")
                            st.rerun()
                        else:
                            st.error(f"❌ Gagal menambahkan: {post_response.text}")
                    else:
                        st.error("⚠️ Data SPV sudah ada. Tidak boleh duplikat.")
                else:
                    st.warning("⚠️ Input tidak boleh kosong.")
            st.write("---")
            
            # ============================
            # 2. Hapus Data (DILETAKKAN DI BAWAH)
            # ============================
            st.subheader("❌ Hapus SPV")
            if not df.empty:
                selected_index = st.selectbox(
                    "Pilih data yang ingin dihapus:",
                    df.index,
                    format_func=lambda i: df.loc[i, "SPV"]
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
