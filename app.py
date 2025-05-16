import streamlit as st
import pandas as pd

st.set_page_config(page_title="ค้นหารายชื่อ", page_icon="🔍")
st.title("🔍 ค้นหารายชื่อใน Google Sheets")

# 📥 ลิงก์ Google Sheets (ต้องเป็นแบบ "แชร์ให้ทุกคนดูได้")
sheet_url = "https://docs.google.com/spreadsheets/d/1S1kpZvIuwa6zX5-ngE8OncIM1PldJEGBeHlT1zLCJj0/export?format=csv&gid=392625625"

# โหลดข้อมูลจาก Google Sheets
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

# 🔎 ช่องค้นหาชื่อ
query = st.text_input("พิมพ์ชื่อหรือคำค้นหา:")

if query:
    # ค้นหาจากทุกคอลัมน์ที่เป็นข้อความ
    result = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]

    if not result.empty:
        st.success(f"พบทั้งหมด {len(result)} รายการ:")
        st.dataframe(result)
    else:
        st.warning("ไม่พบข้อมูลที่ค้นหา")
