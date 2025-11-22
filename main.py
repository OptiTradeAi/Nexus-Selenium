# main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv
import json
from utils import save_capture, DATA_DIR

load_dotenv()

app = FastAPI()

NEXUS_TOKEN = os.getenv("NEXUS_TOKEN", "changeme")

@app.get("/", response_class=PlainTextResponse)
def root():
    return "Nexus Selenium — online"

@app.get("/injector.js", response_class=PlainTextResponse)
def injector_js():
    """
    Serves the injector script (JS) you can load as bookmarklet.
    """
    path = os.path.join(os.path.dirname(__file__), "injector.js")
    if not os.path.exists(path):
        raise HTTPException(404, "injector.js not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/capture")
async def capture(request: Request):
    """
    Receives JSON from the injector running on the HomeBroker page.
    Validates NEXUS_TOKEN header for basic protection.
    """
    token = request.headers.get("X-NEXUS-TOKEN") or request.query_params.get("token")
    if token != NEXUS_TOKEN:
        raise HTTPException(401, "Invalid token")
    payload = await request.json()
    # expected payload: { "url":..., "selectors": {...}, "dom_snapshot": "...", "meta": {...} }
    saved = save_capture(payload)
    return JSONResponse({"status": "ok", "saved": saved})
