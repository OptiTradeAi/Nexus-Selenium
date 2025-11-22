# main.py
import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from selenium_core import start_selenium_loop

app = FastAPI()

NEXUS_TOKEN = "032318"   # Token fixo definido pelo Diego

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus-Selenium",
        "token_loaded": True,
        "email_loaded": os.getenv("HB_EMAIL") is not None
    }

@app.get("/connect")
async def connect(token: str = ""):
    if token != NEXUS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"status": "waiting", "message": "Now open /start to trigger selenium"}

@app.get("/start")
async def start(token: str = ""):
    if token != NEXUS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    start_selenium_loop()
    return {"status": "ok", "message": "Selenium loop started"}
