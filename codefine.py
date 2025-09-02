# app.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Hello Button</title>
</head>
<body>
    <h1>กดปุ่มเพื่อพิมพ์ Hello</h1>
    <button onclick="showMessage()">Say Hello</button>
    <p id="output"></p>
    <script>
        function showMessage() {
            document.getElementById("output").innerText = "Hello!";
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return html_content
