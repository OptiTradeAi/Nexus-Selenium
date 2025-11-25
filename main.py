from fastapi import FastAPI, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os, json

app = FastAPI()

TOKEN = os.getenv("NEXUS_TOKEN", "")
BASE = os.getenv("NEXUS_BASE_URL", "")
CAPTURE_FILE = "/app/data/last_capture.json"

# Servir /static
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
    <head>
      <title>Nexus Entry</title>
      <script src='/static/loader.js?ts={int(os.times()[4])}'></script>
    </head>
    <body>
      <h1>Nexus Selenium Online ✔</h1>
      <p>Token carregado: {TOKEN}</p>
      <p>Clique no bookmarklet para ativar.</p>
    </body>
    </html>
    """


@app.post("/capture")
async def capture(req: Request, x_nexus_token: str = Header(None)):
    if x_nexus_token != TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    data = await req.json()

    try:
        with open(CAPTURE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return JSONResponse({"status": "error", "details": str(e)}, status_code=500)

    return {"status": "ok", "received": True}
