# main.py
import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.getenv("PORT", "10000"))

# Importa a rotina que inicializa o Selenium (ver selenium_core.py)
try:
    from selenium_core import start_selenium_loop
except Exception as e:
    start_selenium_loop = None
    logging.exception("Não foi possível importar start_selenium_loop: %s", e)

app = FastAPI(title="Nexus-Selenium")

@app.on_event("startup")
def startup_event():
    logging.info("Startup event: iniciando selenium loop (se disponível).")
    if callable(start_selenium_loop):
        try:
            start_selenium_loop()
            logging.info("Selenium loop iniciado.")
        except Exception:
            logging.exception("Erro ao iniciar selenium loop.")
    else:
        logging.warning("start_selenium_loop não disponível. Verifique selenium_core.py")

@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <html>
      <head><title>Nexus-Selenium</title></head>
      <body>
        <h2>Nexus Selenium</h2>
        <p>Status: online</p>
        <p>Acesse <a href="/injector">/injector</a> no seu celular para abrir a HomeBroker e iniciar captura.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/capture")
async def capture(request: Request):
    token_header = request.headers.get("X-Nexus-Token") or request.query_params.get("token")
    expected = os.getenv("NEXUS_CAPTURE_SECRET")
    if expected and token_header != expected:
        return JSONResponse(status_code=403, content={"detail": "Invalid token"})
    payload = await request.json()
    os.makedirs("/app/data", exist_ok=True)
    import json, time
    path = f"/app/data/capture_{int(time.time())}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return {"detail": "saved", "path": path}

@app.get("/injector", response_class=HTMLResponse)
def injector():
    html = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Injector</title></head>
      <body>
        <h3>Injector — abra a HomeBroker e inicie captura</h3>
        <p><button onclick="openFrame()">Abrir HomeBroker</button></p>
        <iframe id="hb" src="about:blank" style="width:100%;height:80vh;border:1px solid #ccc"></iframe>
        <script>
        function openFrame(){
          const iframe = document.getElementById('hb');
          iframe.src = "https://www.homebroker.com/pt/sign-in";
        }
        // Opcional: instruções para o usuário executar o bookmarklet/console
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
