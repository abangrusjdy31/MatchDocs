
import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="Pemeriksa Dokumen", layout="wide")
st.title("📄 Pengecekan Kalimat dalam Dokumen PDF")

# Upload dokumen PDF
uploaded_file = st.file_uploader("Upload file PDF", type=["pdf"])

# Input kalimat dari user
kalimat_dicari = st.text_input("Masukkan kalimat yang ingin dicari:")

def is_scanned_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        if page.get_text().strip():
            return False
    return True

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

if uploaded_file and kalimat_dicari:
    file_bytes = uploaded_file.read()
    with st.spinner("🔍 Memproses dokumen..."):
        hasil = process_document(file_bytes, kalimat_dicari)

    st.subheader("📊 Hasil Analisis")
    st.write(f"**Metode ekstraksi:** {hasil['metode']}")
    st.write(f"**Kalimat dicari:** '{hasil['kalimat_dicari']}'") # Corrected line
    st.write(f"**Hasil:** {hasil['hasil']}")

    with st.expander("📄 Lihat seluruh teks dokumen"):
        st.text(hasil['teks'])


