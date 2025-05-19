import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

st.set_page_config(page_title="PDF Reader App", layout="wide")

st.title("📄 แอปอ่าน PDF พร้อมแสดงข้อความและภาพ")

# อัปโหลดไฟล์ PDF
uploaded_file = st.file_uploader("📤 อัปโหลดไฟล์ PDF", type="pdf")

if uploaded_file:
    # เปิด PDF จาก stream
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    # วนแสดงแต่ละหน้า
    for page_number in range(len(doc)):
        page = doc[page_number]

        # แสดงหมายเลขหน้า
        st.subheader(f"📄 หน้า {page_number + 1}")

        # แสดงข้อความ
        text = page.get_text()
        if text.strip():
            st.text_area("📚 ข้อความในหน้านี้", text, height=200)
        else:
            st.warning("⚠️ ไม่พบข้อความในหน้านี้")

        # ดึงและแสดงภาพ
        images = page.get_images(full=True)
        if images:
            st.write("🖼️ ภาพในหน้านี้:")
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption=f"ภาพที่ {img_index + 1}", use_column_width=True)
        else:
            st.info("ไม่มีภาพในหน้านี้")
