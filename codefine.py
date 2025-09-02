# -*- coding: utf-8 -*-
import time
import pandas as pd
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------------
# โหลด Google Sheet สาธารณะ
# -------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1nHnuYP5HKdtuuMjSnABKpJ_xYBOtvtAphYNN7Znb0HI/export?format=csv&id=1nHnuYP5HKdtuuMjSnABKpJ_xYBOtvtAphYNN7Znb0HI&gid=0"
quiz_data = pd.read_csv(sheet_url)

# -------------------------------
# ตั้งค่า Selenium ให้ต่อกับ Chrome ที่เปิดด้วย remote debugging
# -------------------------------
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=options)

# -------------------------------
# ฟังก์ชัน normalize Unicode (สำหรับภาษาไทยตรงตัว)
# -------------------------------
def normalize_unicode(text):
    return unicodedata.normalize('NFC', str(text))

# -------------------------------
# ไฮไลท์คำตอบในเว็บ
# -------------------------------
def highlight_in_web(search_text):
    try:
        driver.execute_script("""
            var searchText = arguments[0].trim();
            if (!searchText) return;

            function highlightLastChar(node, text) {
                var val = node.nodeValue;
                var idx = val.toLowerCase().indexOf(text.toLowerCase());
                if (idx >= 0) {
                    var before = val.substr(0, idx);
                    var match = val.substr(idx, text.length);
                    var after = val.substr(idx + text.length);

                    var mainPart = match.slice(0, -1);
                    var lastChar = match.slice(-1);

                    var spanMain = document.createElement("span");
                    spanMain.textContent = mainPart;

                    var spanLast = document.createElement("span");
                    spanLast.textContent = lastChar;
                    spanLast.style.fontWeight = "bold";
                    spanLast.style.fontSize = "104%";
                    spanLast.style.backgroundColor = "transparent";
                    spanLast.style.color = "inherit";

                    var parent = node.parentNode;
                    parent.insertBefore(document.createTextNode(before), node);
                    parent.insertBefore(spanMain, node);
                    parent.insertBefore(spanLast, node);
                    parent.insertBefore(document.createTextNode(after), node);
                    parent.removeChild(node);
                }
            }

            var walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );

            var node;
            var toProcess = [];
            while (node = walker.nextNode()) {
                if (node.nodeValue.toLowerCase().includes(searchText.toLowerCase())) {
                    toProcess.push(node);
                }
            }

            toProcess.forEach(n => highlightLastChar(n, searchText));
        """, search_text)
        print(f"✅ ทำ highlight แบบเนียน: {search_text}")
    except Exception as e:
        print("⚠️ เกิดข้อผิดพลาด:", e)

# -------------------------------
# วนลูปทำงานอัตโนมัติ
# -------------------------------
print("🚀 เริ่มทำงาน กด Ctrl+C เพื่อหยุด")

try:
    previous_question = ""
    while True:
        try:
            question_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qtext"))
            )
            question_text = question_element.text.strip()

            if question_text != previous_question:
                previous_question = question_text
                print("\n📝 โจทย์ใหม่:", question_text)

                # ดึงคำตอบจาก Google Sheet
                answers = quiz_data[
                    quiz_data['question_text'].apply(lambda x: normalize_unicode(x) == normalize_unicode(question_text))
                ]['answer'].tolist()

                if answers:
                    for ans in answers:
                        highlight_in_web(ans)
                else:
                    print("❌ ไม่เจอคำตอบใน Google Sheet")

            time.sleep(0.5)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(0.5)

except KeyboardInterrupt:
    print("🛑 หยุดการทำงานแล้ว")
