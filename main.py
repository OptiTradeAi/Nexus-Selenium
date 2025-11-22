from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import os
from selenium_core import NexusSelenium

app = FastAPI()

TOKEN = os.getenv("NEXUS_TOKEN")

@app.get("/")
def root():
    return {"status": "online", "service": "Nexus-Selenium"}

@app.get("/start_scan")
def start_scan(token: str):
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    try:
        nexus = NexusSelenium()
        nexus.start()

        return HTMLResponse("""
        <html>
        <body style='font-family: Arial; background:#111; color:#0f0; padding:20px'>
        <h2>Nexus Selenium – Modo SCAN Ativado</h2>
        <p>O agente está abrindo a corretora e iniciando a análise.</p>
        <p>Mantenha esta aba aberta por enquanto.</p>
        </body>
        </html>
        """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
