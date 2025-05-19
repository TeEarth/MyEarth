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
    return pipeline("question-answering", model="deepset/xlm-roberta-base-squad2")

model = load_model()
qa_model = load_qa_model()

# เก็บข้อความทั้งหมด
all_lines = []
page_map = []

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        # แยกเป็น "บรรทัด"
        for line in text.splitlines():
            clean_line = line.strip()
            if clean_line:
                all_lines.append(clean_line)
                page_map.append(page_number + 1)

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

    # 🔍 AI: ค้นหาบรรทัดที่ใกล้เคียงคำถาม
    if all_lines:
        st.markdown("---")
        st.header("❓ ถาม-ตอบจากเนื้อหา PDF ด้วย AI")
        user_question = st.text_input("💬 พิมพ์คำถามของคุณที่นี่")

        # สร้างเวกเตอร์ของแต่ละบรรทัด
        embeddings = model.encode(all_lines)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))

        if user_question:
            # เวกเตอร์ของคำถาม
            question_vec = model.encode([user_question])
            D, I = index.search(np.array(question_vec), k=3)

            st.subheader("🔎 บรรทัดที่เกี่ยวข้องมากที่สุด:")
            for rank, idx in enumerate(I[0]):
                st.markdown(f"**อันดับ {rank + 1}** (หน้า {page_map[idx]})")
                st.success(all_lines[idx])

            # ใช้ context ที่ใกล้ที่สุดตอบคำถาม
            context = all_lines[I[0][0]]
            with st.spinner("🤖 AI กำลังสกัดคำตอบ..."):
                result = qa_model(question=user_question, context=context)
                answer = result['answer']

            st.markdown("---")
            st.subheader("✅ คำตอบจาก AI:")
            st.success(answer)
