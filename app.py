import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline
from pythainlp.tokenize import word_tokenize

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

def jaccard_similarity(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    if not union:
        return 0
    return len(intersection) / len(union)

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

            # ตัดคำคำถามเป็น tokens
            question_tokens = word_tokenize(user_question.lower())

            matched_lines = []
            for idx, line in enumerate(all_lines):
                # รวมบรรทัดก่อนหน้าและหลัง (ถ้ามี) มาเช็คด้วย
                lines_to_check = [line]
                if idx > 0:
                    lines_to_check.insert(0, all_lines[idx - 1])
                if idx < len(all_lines) - 1:
                    lines_to_check.append(all_lines[idx + 1])

                # ตัดคำของบรรทัดที่ตรวจสอบทั้งหมด
                tokens_to_check = []
                for l in lines_to_check:
                    tokens_to_check.extend(word_tokenize(l.lower()))

                # คำนวณ similarity
                sim = jaccard_similarity(question_tokens, tokens_to_check)

                if sim >= 0.7:  # มากกว่าหรือเท่ากับ 70%
                    matched_lines.append((line, page_map[idx], sim))

            if matched_lines:
                # เรียงลำดับตามความเหมือนมากสุด
                matched_lines.sort(key=lambda x: x[2], reverse=True)
                for i, (matched_line, page_num, similarity) in enumerate(matched_lines[:5]):  # แสดงสูงสุด 5 บรรทัด
                    st.markdown(f"**{i+1}.** (หน้า {page_num}) ความเหมือน: {similarity:.2%}")
                    st.success(matched_line)
            else:
                st.info("ไม่พบข้อความที่เกี่ยวข้องกับคำถาม")

            st.markdown("---")
            st.subheader("✅ คำตอบจาก AI:")
            # นำบรรทัดที่เหมือนที่สุดมาให้ AI ตอบ
            if matched_lines:
                context = matched_lines[0][0]
                result = qa_model(question=user_question, context=context)
                answer = result.get('answer', 'ไม่พบคำตอบที่ชัดเจน')
                st.success(answer)
            else:
                st.info("ไม่สามารถหาคำตอบจากเอกสารได้")
