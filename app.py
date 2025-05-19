import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image
from sentence_transformers import SentenceTransformer
import numpy as np
from transformers import pipeline
from nltk.tokenize import word_tokenize

# ฟังก์ชันคำนวณ Jaccard similarity
def jaccard_similarity(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    if not set1 or not set2:
        return 0
    return len(set1.intersection(set2)) / len(set1.union(set2))

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

    # เก็บประวัติคำถาม-คำตอบใน session state
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []

    st.markdown("---")
    st.header("❓ ถาม-ตอบจากเนื้อหา PDF ด้วย AI")

    user_question = st.text_input("💬 พิมพ์คำถามของคุณที่นี่")

    if user_question:
        question_tokens = user_question.lower().split()
        matched_lines = []
        matched_indices = set()
        thresholds = [0.7, 0.6, 0.5]

        for threshold in thresholds:
            for idx, line in enumerate(all_lines):
                if idx in matched_indices:
                    continue
                lines_to_check = [line]
                if idx > 0:
                    lines_to_check.insert(0, all_lines[idx - 1])
                if idx < len(all_lines) - 1:
                    lines_to_check.append(all_lines[idx + 1])

                tokens_to_check = []
                for l in lines_to_check:
                    tokens_to_check.extend(word_tokenize(l.lower()))

                sim = jaccard_similarity(question_tokens, tokens_to_check)
                if sim >= threshold:
                    matched_lines.append((line, page_map[idx], sim))
                    matched_indices.add(idx)

            if len(matched_lines) >= 5:
                break

        if matched_lines:
            matched_lines.sort(key=lambda x: x[2], reverse=True)
            st.subheader("🔎 บรรทัดที่เกี่ยวข้องสูงสุด:")
            for i, (matched_line, page_num, similarity) in enumerate(matched_lines[:5]):
                st.markdown(f"**{i+1}.** (หน้า {page_num}) ความเหมือน: {similarity:.2%}")
                st.success(matched_line)

            # ใช้บรรทัดที่เหมือนที่สุดเป็น context ถามโมเดล AI
            context = matched_lines[0][0]
            result = qa_model(question=user_question, context=context)
            answer = result.get('answer', 'ไม่พบคำตอบที่ชัดเจน')

        else:
            st.info("ไม่พบข้อความที่เกี่ยวข้องกับคำถาม")
            answer = "ไม่พบคำตอบที่ชัดเจนในเอกสาร"

        # เก็บคำถาม-คำตอบใน session state
        st.session_state.qa_history.append({"question": user_question, "answer": answer})

    # แสดงประวัติถาม-ตอบทั้งหมด
    if st.session_state.qa_history:
        st.markdown("---")
        st.header("💬 ประวัติถาม-ตอบของคุณ")
        for i, qa in enumerate(st.session_state.qa_history):
            st.markdown(f"**คำถาม {i+1}:** {qa['question']}")
            st.markdown(f"**คำตอบ:** {qa['answer']}")

