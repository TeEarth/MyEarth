import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

st.set_page_config(page_title="PDF AI Q&A App", layout="wide")
st.title("📄 แอปอ่าน PDF + ถามตอบด้วย AI")

uploaded_file = st.file_uploader("📤 อัปโหลดไฟล์ PDF", type="pdf")

# โหลดโมเดลฝังข้อความ
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# เก็บข้อความทั้งหมด
all_text_blocks = []
page_text_map = []  # เก็บหน้าที่ของข้อความ

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        # แยกข้อความเป็นบล็อก
        for block in text.split("\n\n"):
            clean_block = block.strip()
            if clean_block:
                all_text_blocks.append(clean_block)
                page_text_map.append(page_number + 1)

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
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption=f"ภาพที่ {img_index + 1}", use_column_width=True)
        else:
            st.info("ไม่มีภาพในหน้านี้")

    # 🔎 AI: สร้าง embedding และ FAISS index
    if all_text_blocks:
        st.markdown("---")
        st.header("❓ ถาม-ตอบจากเนื้อหา PDF ด้วย AI")
        user_question = st.text_input("💬 พิมพ์คำถามของคุณที่นี่")

        # สร้างเวกเตอร์จากข้อความใน PDF
        embeddings = model.encode(all_text_blocks)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))

        if user_question:
            # สร้างเวกเตอร์ของคำถาม
            question_vec = model.encode([user_question])
            D, I = index.search(np.array(question_vec), k=3)  # คืน 3 อันดับที่ใกล้เคียงที่สุด

            st.subheader("🔎 ข้อความที่เกี่ยวข้องที่สุด:")
            for rank, idx in enumerate(I[0]):
                st.markdown(f"**อันดับ {rank + 1}** (หน้า {page_text_map[idx]})")
                st.success(all_text_blocks[idx])
