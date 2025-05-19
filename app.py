import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

st.set_page_config(page_title="PDF Reader App", layout="wide")
st.title("📄 แอปอ่าน PDF พร้อมแสดงข้อความและภาพ")

uploaded_file = st.file_uploader("📤 อัปโหลดไฟล์ PDF", type="pdf")

# เก็บข้อความทั้งหมดจาก PDF
all_text_blocks = []

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        # บันทึกข้อความแบ่งเป็นบล็อก (ย่อหน้า)
        for block in text.split("\n\n"):
            clean_block = block.strip()
            if clean_block:
                all_text_blocks.append((page_number + 1, clean_block))

        # แสดงข้อความและภาพ
        st.subheader(f"📄 หน้า {page_number + 1}")
        if text.strip():
            st.text_area("📚 ข้อความในหน้านี้", text, height=200)
        else:
            st.warning("⚠️ ไม่พบข้อความในหน้านี้")

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

    # 🔍 ช่องใส่คำถาม
    st.markdown("---")
    st.header("❓ ถาม-ตอบจากเนื้อหา PDF")
    user_question = st.text_input("💬 พิมพ์คำถามของคุณที่นี่ (เช่น 'สาเหตุของ...')")

    if user_question:
        st.subheader("🔎 ข้อความที่ใกล้เคียงกับคำถาม:")
        matches = []

        for page_num, block in all_text_blocks:
            if any(word in block for word in user_question.split()):
                matches.append((page_num, block))

        if matches:
            for page_num, match_text in matches:
                st.markdown(f"📄 หน้า {page_num}")
                st.success(match_text)
        else:
            st.warning("ไม่พบข้อความที่ใกล้เคียงกับคำถาม")
