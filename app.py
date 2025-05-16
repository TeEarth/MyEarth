import streamlit as st
import datetime
import locale

# ตั้งค่า locale ภาษาไทย (อาจใช้ไม่ได้ในบางระบบ)
try:
    locale.setlocale(locale.LC_TIME, 'th_TH.UTF-8')
except:
    locale.setlocale(locale.LC_TIME, '')

st.set_page_config(page_title="วันนี้วันอะไร", page_icon="📅")

st.title("📅 วันนี้วันอะไร")

# แสดงวัน
now = datetime.datetime.now()
today_text = now.strftime("%A ที่ %d %B %Y")
st.markdown(f"## 👉 {today_text}")

# 🔹 ช่องกรอกชื่อ-นามสกุล
fullname = st.text_input("👤 กรุณากรอกชื่อ-นามสกุล")

# 🔹 เลือกเพศจากกล่องข้อความ
gender = st.selectbox("⚧ กรุณาเลือกเพศ", ["ชาย", "หญิง", "ไม่ระบุ"])

# 🔹 แสดงผลเมื่อกรอกข้อมูลครบ
if fullname:
    st.success(f"ยินดีต้อนรับคุณ **{fullname}** ({gender})")
