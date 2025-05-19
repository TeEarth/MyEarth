import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline

st.set_page_config(page_title="PDF AI Q&A App", layout="wide")
st.title("📄 แอปอ่าน PDF + ถามตอบด้วย AI")

uploaded_file = st.file_uploader("📤 อัปโหลดไฟล์ PDF", type="pdf")

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def load_qa_model():
    return pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

model = load_model()
qa_model = load_qa_model()

all_lines = []
page_map = []

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        for line in text.splitlines():
            clean_line = line.strip()
            if clean_line:
                all_lines.append(clean_line)
                page_map.append(page_number + 1)

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
                st.image(image, caption=f"ภาพที่ {img_index + 1}", use_container_width=True)
        else:
            st.info("ไม่มีภาพในหน้านี้")

    if all_lines:
        st.markdown("---")
        st.header("❓ ถาม-ตอบจากเนื้อหา PDF ด้วย AI")
        user_question = st.text_input("💬 พิมพ์คำถามของคุณที่นี่")

        embeddings = model.encode(all_lines)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))

        if user_question:
            st.subheader("🔎 บรรทัดที่มีคำถามหรือคำที่เกี่ยวข้อง:")
        
            # ทำให้คำถามเป็นคำเล็กทั้งหมด (lowercase) เพื่อให้ค้นหาแบบไม่สนใจตัวพิมพ์ใหญ่เล็ก
            question_lower = user_question.lower()
        
            # ค้นหาบรรทัดที่มีคำที่ตรงกับคำถาม (คำที่ปรากฏในคำถาม)
            matched_lines = []
            for idx, line in enumerate(all_lines):
                # แปลงบรรทัดเป็น lowercase
                line_lower = line.lower()
        
                # ถ้าคำถามอยู่ในบรรทัดนั้น (ตรวจสอบแบบง่ายๆ)
                if any(word in line_lower for word in question_lower.split()):
                    matched_lines.append((line, page_map[idx]))
        
            if matched_lines:
                for i, (matched_line, page_num) in enumerate(matched_lines[:5]):  # แสดงสูงสุด 5 บรรทัด
                    st.markdown(f"**{i+1}.** (หน้า {page_num}) {matched_line}")
            else:
                st.info("ไม่พบข้อความที่เกี่ยวข้องกับคำถาม")

            st.markdown("---")
            st.subheader("✅ คำตอบจาก AI:")
