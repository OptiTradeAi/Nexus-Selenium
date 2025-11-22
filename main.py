# main.py
from fastapi import FastAPI, HTTPException
import os
from selenium_core import start_selenium_loop

app = FastAPI()

NEXUS_TOKEN = "032318"


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus-Selenium",
        "token_loaded": True
    }


@app.get("/connect")
async def connect(token: str = ""):
    if token != NEXUS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"status": "waiting", "step": "use /start to launch selenium"}


@app.get("/start")
async def start(token: str = ""):
    if token != NEXUS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    start_selenium_loop()

    return {"status": "ok", "message": "selenium started"}
