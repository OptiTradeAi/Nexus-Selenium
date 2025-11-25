# main.py
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime

app = FastAPI()

# Diretório para armazenar capturas
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Token de verificação (defina via environment variable NEXUS_TOKEN no Render)
NEXUS_TOKEN = os.getenv("NEXUS_TOKEN", "")

# Serve arquivos estáticos (injector.html + assets se houver)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    # Redireciona para injector (arquivo estático)
    index_path = os.path.join("static", "injector.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<h3>Injector not found. Put injector.html in /static</h3>", status_code=404)


@app.post("/capture")
async def capture(request: Request, x_nexus_token: str | None = Header(None)):
    """
    Recebe o JSON com metadados do scanner.
    Exige header X-NEXUS-TOKEN com o token configurado no Render para autenticação.
    """
    if not NEXUS_TOKEN:
        raise HTTPException(status_code=500, detail="Server misconfigured: NEXUS_TOKEN not set on server.")
    if x_nexus_token != NEXUS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Enforce we do NOT receive credentials - if present, reject (safety)
    if isinstance(payload, dict) and ("username_value" in payload or "password_value" in payload):
        # defensive: never accept credential values
        raise HTTPException(status_code=400, detail="Credentials not allowed in payload")

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"capture_{ts}.json"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return JSONResponse({"status": "ok", "saved": filename})


@app.get("/captures")
async def list_captures():
    """Lista arquivos no diretório /app/data"""
    files = []
    for f in sorted(os.listdir(DATA_DIR), reverse=True):
        if f.endswith(".json"):
            files.append({
                "file": f,
                "path": f"/data/{f}"
            })
    return {"captures": files}


@app.get("/data/{filename}")
async def get_capture_file(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="application/json")
