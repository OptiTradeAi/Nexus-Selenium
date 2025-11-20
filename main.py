from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading
import os
import time

from agent import start_agent

app = FastAPI()

# ==========================
#       ENDPOINT ROOT
# ==========================
@app.get("/")
def root():
    return {"status": "Nexus Selenium ONLINE", "version": "1.0.0"}


# ==========================
#       START SCAN
# ==========================
@app.get("/start_scan")
def start_scan():
    """
    Inicia o processo do Selenium em thread separada.
    """
    try:
        def run_agent():
            start_agent()

        # Inicia thread paralela para não travar a API
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

        return JSONResponse(
            {"status": "ok",
             "detail": "Nexus Selenium iniciado. Abra o navegador e faça login na HomeBroker."},
            status_code=200
        )

    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)
