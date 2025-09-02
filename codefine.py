# codefine.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# หน้าเว็บหลัก
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Hello Button</title>
</head>
<body>
    <h1>กดปุ่มเพื่อพิมพ์ Hello</h1>
    <form action="/hello" method="get">
        <button type="submit">Say Hello</button>
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return html_content

@app.get("/hello")
async def say_hello():
    # ทำงาน Python ที่คุณต้องการ เช่น พิมพ์ลง console
    print("Hello")  
    return HTMLResponse("<h2>คุณกดปุ่มแล้ว! กลับไปหน้า <a href='/'>หน้าแรก</a></h2>")
