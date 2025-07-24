import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="Pemeriksa Dokumen ZIP", layout="wide")
st.title("📦 Pengecekan Kalimat dalam Dokumen PDF dari ZIP")

# Upload file ZIP
uploaded_archive = st.file_uploader("Upload file .zip berisi PDF", type=["zip"])
kalimat_dicari = st.text_input("Masukkan kalimat yang ingin dicari:")

# Fungsi untuk cek apakah PDF hasil scan (tanpa teks)
def is_scanned_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        if page.get_text().strip():
            return False
    return True

# Fungsi untuk ekstrak teks (OCR jika perlu)
def extract_text(file_bytes, use_ocr=False):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    result = ""
    for page in doc:
        if use_ocr:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes()))
            text = pytesseract.image_to_string(img, lang='ind')
        else:
            text = page.get_text()
        result += text + "\n"
    return result

# Fungsi memproses 1 file PDF
def process_document(file_bytes, kalimat_dicari):
    scanned = is_scanned_pdf(file_bytes)
    metode = "OCR (dokumen hasil scan)" if scanned else "Ekstraksi langsung (dokumen teks)"
    extracted_text = extract_text(file_bytes, use_ocr=scanned)

    if kalimat_dicari.lower() in extracted_text.lower():
        hasil = "✅ Kalimat ditemukan dalam dokumen."
    else:
        hasil = "❌ Kalimat tidak ditemukan."

    return {
        "metode": metode,
        "kalimat_dicari": kalimat_dicari,
        "hasil": hasil,
        "teks": extracted_text
    }

# Fungsi untuk mengekstrak PDF dari ZIP
def extract_pdfs_from_zip(uploaded_file):
    pdf_files = {}
    with zipfile.ZipFile(uploaded_file) as z:
        for name in z.namelist():
            if name.lower().endswith(".pdf"):
                with z.open(name) as file:
                    pdf_files[name] = file.read()
    return pdf_files

# Proses utama
if uploaded_archive and kalimat_dicari:
    with st.spinner("📦 Mengekstrak file dari ZIP..."):
        try:
            pdf_files = extract_pdfs_from_zip(uploaded_archive)
        except Exception as e:
            st.error(f"Gagal membaca arsip: {e}")
            st.stop()

    if not pdf_files:
        st.warning("Tidak ada file PDF ditemukan di dalam arsip.")
    else:
        st.success(f"{len(pdf_files)} file PDF ditemukan.")
        selected_files = st.multiselect("Pilih file PDF yang ingin dianalisis:", list(pdf_files.keys()))

        for filename in selected_files:
            st.markdown(f"### 📘 {filename}")
            with st.spinner(f"🔍 Memeriksa dokumen: {filename}"):

                result = process_document(pdf_files[filename], kalimat_dicari)
                st.write(f"**Metode ekstraksi:** {result['metode']}")
                st.write(f"**Hasil:** {result['hasil']}")

                with st.expander("📄 Lihat seluruh teks dokumen"):
                    st.text(result['teks'])
