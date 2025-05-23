import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ตั้งค่า credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheet และเลือก sheet ชื่อ "Special Force"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1lbHvC-_tkGBKvF7Wc5Yl-vHzMKfRnvPkqiKrGdk5Vtk/edit#gid=509666436"
sheet = client.open_by_url(spreadsheet_url).worksheet("Special Force")

# ดึงข้อมูลทั้งหมด
data = sheet.get_all_values()  # ข้อมูลทั้งหมดเป็น list of lists

# ส่วนหัว (หัวตาราง)
headers = data[0]
rows = data[1:]

# UI ด้วย Streamlit
st.title("ถาม-ตอบ จากชีต Special Force")
question = st.text_input("พิมพ์คำถามที่ต้องการค้นหา:")

if question:
    found = False
    for row in rows:
        if row[0].strip() == question.strip():  # เทียบคอลัมน์ A
            st.success(f"คำตอบ: {row[1]}")  # แสดงคอลัมน์ B
            found = True
            break
    if not found:
        st.warning("ไม่พบคำถามนี้ในชีต Special Force")
