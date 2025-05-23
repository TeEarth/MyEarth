import streamlit as st
import pandas as pd

# โหลดข้อมูลจากไฟล์ Excel
@st.cache_data
def load_data():
    df = pd.read_excel("Special.xlsx", sheet_name="Special Force", engine="openpyxl")
    return df

df = load_data()

# ส่วนของแอพ
st.title("ถาม-ตอบ จากไฟล์ Excel")
question = st.text_input("พิมพ์คำถามที่ต้องการค้นหา:")

if question:
    match = df[df.iloc[:, 0].astype(str).str.strip() == question.strip()]
    if not match.empty:
        answer = match.iloc[0, 1]  # คำตอบจากคอลัมน์ที่ 2 (B)
        st.success(f"คำตอบ: {answer}")
    else:
        st.warning("ไม่พบคำถามนี้ในไฟล์ Excel")
