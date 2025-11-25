from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json, os

app = FastAPI()

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


# Página inicial → serve o injector.html
@app.get("/")
async def index():
    return FileResponse("injector.html")


# Endpoint para receber dados do scanner
@app.post("/capture")
async def capture(request: Request):
    data = await request.json()

    os.makedirs("data", exist_ok=True)

    with open("data/capture.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("[NEXUS] Dados recebidos do scanner:", data.keys())

    return JSONResponse({"status": "ok"})
