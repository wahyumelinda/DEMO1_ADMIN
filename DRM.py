import pandas as pd
import streamlit as st
from fpdf import FPDF

# 1. LINK CSV dari Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1z5o3P6nxcYMRz23EYUnjkLJUAKpOIkpe7-YI11mt4Ps/export?format=csv&gid=0"

# 2. Ambil dua baris header
df = pd.read_csv(sheet_url, header=[0, 1])

# 3. Gabungkan multi-header jadi 1 kolom nama
df.columns = [' '.join([str(a).strip(), str(b).strip()]).strip() for a, b in df.columns]
df.columns = df.columns.str.replace('\s+', ' ', regex=True)  # hapus spasi berlebih

# 4. Reset index (jaga-jaga)
df = df.reset_index(drop=True)

# 5. Pilih kolom ID dan tampilkan opsi
st.title("🖨️ Cetak PDF Riwayat Mesin")
kolom_id = [col for col in df.columns if "id" in col.lower()][0]  # cari kolom ID otomatis
id_terpilih = st.selectbox("Pilih ID Riwayat Mesin", df[kolom_id].dropna().unique())
row = df[df[kolom_id] == id_terpilih].iloc[0]

from textwrap import wrap

def buat_pdf(row):
    pdf = FPDF("L", "mm", "A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "PT. ULTRA PRIMA ABADI", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"BU: {row.get('BU Unnamed: 1_level_1', '')}   |   Mesin: {row.get('Mesin Unnamed: 4_level_1', '')}   |   Tanggal: {row.get('Tanggal Pengerjaan Unnamed: 6_level_1', '')}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "DAFTAR RIWAYAT MESIN", ln=True, align="C")
    pdf.ln(3)

    headers = [
        "Tanggal", "Produk", "Mulai", "Selesai", "Masalah",
        "Tindakan Perbaikan", "Deskripsi Sparepart", "Qty", "PIC"
    ]
    col_widths = [25, 30, 18, 18, 30, 45, 60, 15, 30]
    isi_data = [
        str(row.get("Tanggal Pengerjaan Unnamed: 6_level_1", "")),
        str(row.get("Produk Unnamed: 3_level_1", "")),
        str(row.get("Pengerjaan Mulai", "")),
        str(row.get("Unnamed: 8_level_0 Selesai", "")),
        str(row.get("Masalah Unnamed: 9_level_1", "")),
        str(row.get("Tindakan Perbaikan Unnamed: 10_level_1", "")),
        str(row.get("Pemakaian Sparepart Deskripsi", "")),
        str(row.get("Unnamed: 12_level_0 Quantity", "")),
        str(row.get("PIC Unnamed: 13_level_1", ""))
    ]

    # Print Header
    pdf.set_font("Arial", "B", 10)
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 8, headers[i], border=1, align="C")
    pdf.ln()

    # Wrap text secara manual agar multi-line tetap sejajar
    # Perbaikan agar newline tetap dianggap baris baru, dan tiap baris di-wrap otomatis
    pdf.set_font("Arial", "", 10)
    wrapped_cells = []
    max_lines = 0

    for i in range(len(isi_data)):
        baris_baru = isi_data[i].split('\n')  # Split berdasarkan enter
        hasil_wrap = []

        for baris in baris_baru:
            hasil_wrap.extend(wrap(baris, width=int(col_widths[i] / 2.5)))  # Wrap tiap baris
            hasil_wrap.append("")  # spasi antar paragraf
        wrapped_cells.append(hasil_wrap)

        if len(hasil_wrap) > max_lines:
            max_lines = len(hasil_wrap)



    line_height = 6
    row_height = max_lines * line_height

    # Render semua baris dengan kombinasi \n dan wrapping otomatis
    x_start = pdf.get_x()
    y_start = pdf.get_y()

    for line_idx in range(max_lines):
        x = x_start
        for col_idx in range(len(wrapped_cells)):
            pdf.set_xy(x, y_start + line_idx * line_height)

            # Cek apakah baris ini ada pada cell tersebut
            if line_idx < len(wrapped_cells[col_idx]):
                isi_baris = wrapped_cells[col_idx][line_idx]
                # Pakai multi_cell untuk auto-wrap jika isi_baris panjang
                pdf.multi_cell(col_widths[col_idx], line_height, isi_baris, border=0)
            else:
                # Kosongkan jika tidak ada baris
                pdf.multi_cell(col_widths[col_idx], line_height, "", border=0)
            
            x += col_widths[col_idx]

            
    # Gambar border setelah isi semua baris
    pdf.set_xy(x_start, y_start)
    for i in range(len(headers)):
        pdf.rect(x_start + sum(col_widths[:i]), y_start, col_widths[i], row_height)

    pdf.set_y(y_start + row_height + 2)

    # Footer
    pdf.ln(10)
    pdf.cell(0, 8, "Dibuat oleh,", ln=True)
    pdf.cell(60, 8, "Spv Shift 1", ln=False)
    pdf.cell(60, 8, "Spv Shift 2", ln=False)
    pdf.cell(60, 8, "Spv Shift 3", ln=True)
    pdf.ln(20)
    pdf.cell(0, 8, "Mengetahui,", ln=True)
    pdf.cell(60, 8, "SM Teknik", ln=True)

    return pdf.output(dest="S").encode("latin-1")


# 7. Tombol Download
pdf_file = buat_pdf(row)
st.download_button(
    label="📥 Download PDF",
    data=pdf_file,
    file_name=f"Riwayat_Mesin_ID_{id_terpilih}.pdf",
    mime="application/pdf"
)
# Lihat nama-nama kolom setelah digabung
# st.write("📌 Nama kolom final:")
# st.write(df.columns.tolist())