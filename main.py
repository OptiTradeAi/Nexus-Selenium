from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Token
BACKEND_TOKEN = os.getenv("TOKEN", "032318")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return HTMLResponse("""
    <h1>NEXUS-Selenium Backend Ativo</h1>
    <p>Use o bookmarklet na corretora para enviar os dados.</p>
    """)


@app.get("/hb")
def hb_redirect():
    return HTMLResponse("""
        <script>
            window.location.href = "https://www.homebroker.com/pt/sign-in";
        </script>
    """)


@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}


@app.post("/capture")
async def capture(request: Request):
    token = request.headers.get("X-Nexus-Token")

    if token != BACKEND_TOKEN:
        return JSONResponse({"error": "Invalid token"}, status_code=403)

    data = await request.json()
    print("📩 CAPTURE RECEBIDA:", data)

    return {"status": "ok", "received": data}
