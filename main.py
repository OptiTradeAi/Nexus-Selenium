from fastapi import FastAPI, Request, HTTPException
import os
import uvicorn
from selenium_core import perform_dom_learning

app = FastAPI()

# =====================================================
# CONFIGURAÇÕES CARREGADAS DO ENV
# =====================================================
NEXUS_TOKEN = os.environ.get("NEXUS_TOKEN", "Dcrt17*")
CAPTURE_OUTPUT = "/app/data/capture.json"


def verify_token(token: str):
    return token == NEXUS_TOKEN


# =====================================================
# ENDPOINT PRINCIPAL (STATUS)
# =====================================================
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus-Selenium",
        "token_loaded": bool(NEXUS_TOKEN),
        "email_loaded": bool(os.environ.get("HB_EMAIL"))
    }


# =====================================================
# INICIA O MODO DE SCAN
# =====================================================
@app.post("/start_scan")
async def start_scan(request: Request):
    token = request.query_params.get("token")
    if not verify_token(token):
        raise HTTPException(status_code=403, detail="Token inválido")

    # chama o módulo selenium_core
    result = perform_dom_learning()
    return {"status": "scan_started", "result": result}


# =====================================================
# RECEBE CAPTURA (FUTURO, EXTENSÃO)
# =====================================================
@app.post("/capture")
async def capture_data(request: Request):
    token = request.query_params.get("token")
    if not verify_token(token):
        raise HTTPException(status_code=403, detail="Token inválido")

    body = await request.json()
    with open(CAPTURE_OUTPUT, "w") as f:
        import json
        json.dump(body, f, indent=4)

    return {"status": "capture_saved"}


# =====================================================
# START SERVER
# =====================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
