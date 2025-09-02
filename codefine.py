# app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# หน้า HTML
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
    print("Hello")  # พิมพ์ลง console ของเซิร์ฟเวอร์
    return HTMLResponse("<h2>คุณกดปุ่มแล้ว! กลับไปหน้า <a href='/'>หน้าแรก</a></h2>")
