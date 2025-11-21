import os
from fastapi import FastAPI
from agent import start_agent
import threading

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "ok",
        "detail": "Nexus Selenium rodando."
    }

@app.get("/start_agent")
def start_background():
    t = threading.Thread(target=start_agent)
    t.daemon = True
    t.start()
    return {"status": "ok", "detail": "Agente iniciado."}
