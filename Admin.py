import streamlit as st


# Konfigurasi halaman utama
st.set_page_config(page_title="Admin", page_icon="🔐")

# Inisialisasi session_state untuk status login admin
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
    
# Tampilan awal: input kode akses
if not st.session_state.admin_logged_in:
    st.title("🔐 Halaman Akses Admin")
    access_code_input = st.text_input("🔑 Masukkan Kode Akses", type="password")
    submit_code = st.button("🔍 Verifikasi")

    if submit_code:
        if access_code_input == "kode_aman_admin":
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("❌ Kode akses salah. Silakan coba lagi.")

# Jika sudah login sebagai admin
if st.session_state.admin_logged_in:
    st.title("👨‍💼 Panel Admin")
    
    page = st.selectbox(
        "Pilih Halaman",
        [
            "📋 Dashboard Admin",
            "➕ Register Akun",
            "🗂️ BU",
            "🗂️ Line",
            "🗂️ Masalah",
            "🗂️ Mesin",
            "🗂️ PIC",
            "🗂️ Produk",
            "🗂️ SPV",
            "🗂️ SM",
        ]
    )

    # Routing ke halaman sesuai pilihan
    if page == "📋 Dashboard Admin":
        st.title("")

    elif page == "➕ Register Akun":
        import register
        register.run()

    elif page == "🗂️ BU":
        import BU
        BU.run()

    elif page == "🗂️ Line":
        import Line
        Line.run()

    elif page == "🗂️ Masalah":
        import Masalah
        Masalah.run()

    elif page == "🗂️ Mesin":
        import Mesin
        Mesin.run()

    elif page == "🗂️ PIC":
        import PIC
        PIC.run()

    elif page == "🗂️ Produk":
        import Produk
        Produk.run()

    elif page == "🗂️ SPV":
        import SPV
        SPV.run()

    elif page == "🗂️ SM":
        import SM
        SM.run()
