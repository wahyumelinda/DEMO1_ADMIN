import streamlit as st
import pandas as pd
import requests

# 🔗 Ganti ini dengan URL Web App dari Apps Script kamu
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzN1pW0dkBl4y0bOrDEYoqXuviUSmmnI1Pqp_fxa2p4PjZAzGAAv_u7CLBenDaHPzYFbg/exec"

def run():
    # ============================
    # 1. Tampilkan isi Sheet "Line"
    # ============================
    st.subheader("📋 Manajemen Data Sheet 'Line'")
    df_line = pd.DataFrame()

    try:
        line_response = requests.get(WEB_APP_URL + "?sheet=Line")
        if line_response.status_code == 200:
            line_data = line_response.json()
            df_line = pd.DataFrame(line_data, columns=["BU", "Line"])
            st.dataframe(df_line, use_container_width=True)
        else:
            st.warning(f"Gagal mengambil data Line: {line_response.status_code}")
    except Exception as e:
        st.error(f"❌ Error mengambil data Line: {e}")
    st.write("---")
    
    # ============================
    # 2. Form Tambah Data ke Line
    # ============================
    st.subheader("➕ Tambah Line Baru")

    # Ambil dropdown SC dari sheet BU
    sc_list = []
    try:
        bu_response = requests.get(WEB_APP_URL + "?sheet=BU")
        if bu_response.status_code == 200:
            sc_list = bu_response.json()
        else:
            st.warning("Gagal ambil data dari Sheet BU.")
    except Exception as e:
        st.warning(f"⚠️ Error ambil BU: {e}")

    if sc_list:
        selected_sc = st.selectbox("Pilih BU)", sc_list)
        new_line = st.text_input("Masukkan Nama Line (misal: Line 1)")

    if st.button("📝 Tambahkan ke Sheet Line"):
        if new_line.strip():
            # Validasi duplikat: cek apakah SC-Line sudah ada
            new_pair = (selected_sc.strip().lower(), new_line.strip().lower())
            existing_pairs = df_line.apply(lambda row: (str(row['BU']).strip().lower(), str(row['Line']).strip().lower()), axis=1).tolist()

            if new_pair in existing_pairs:
                st.warning("⚠️ Kombinasi BU dan Line ini sudah ada. Duplikat tidak diizinkan.")
            else:
                payload = {"sc": selected_sc, "line": new_line.strip()}
                response = requests.post(WEB_APP_URL + "?func=addLine", json=payload)

                if response.status_code == 200 and "Line Added" in response.text:
                    st.success("✅ Baris berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.error(f"❌ Gagal menambahkan: {response.text}")
        else:
            st.warning("⚠️ Nama Line tidak boleh kosong.")

    st.write("---")
    
    # ============================
    # 3. Hapus Baris dari Line
    # ============================
    st.subheader("❌ Hapus Line")

    if not df_line.empty:
        label_list = df_line.apply(lambda row: f"{row['BU']} - {row['Line']}", axis=1)
        selected_index = st.selectbox(
            "Pilih baris yang ingin dihapus:",
            df_line.index,
            format_func=lambda i: label_list[i]
        )

        if st.button("🗑️ Hapus Baris"):
            payload = {"index": int(selected_index)}
            delete_response = requests.post(WEB_APP_URL + "?func=deleteLine", json=payload)

            if delete_response.status_code == 200 and "Deleted" in delete_response.text:
                st.success("✅ Baris berhasil dihapus.")
                st.rerun()
            else:
                st.error(f"❌ Gagal menghapus: {delete_response.text}")
