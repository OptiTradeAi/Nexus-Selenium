# main.py
import os
import json
from fastapi import FastAPI, Request, Header
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional

app = FastAPI()

# Token (env)
BACKEND_TOKEN = os.getenv("NEXUS_TOKEN", "032318")

# Static files (static/ must exist)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    # redirect user directly to HomeBroker login page (useful for manual tests)
    return RedirectResponse("https://www.homebroker.com/pt/sign-in")

@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}

# Endpoint to receive arbitrary captures from client-side scripts
@app.post("/capture")
async def capture(payload: Request, x_nexus_token: Optional[str] = Header(None)):
    try:
        if x_nexus_token != BACKEND_TOKEN:
            return JSONResponse({"error": "invalid token"}, status_code=403)
        data = await payload.json()
        # Save capture with timestamp
        os.makedirs("/app/data/captures", exist_ok=True)
        fname = f"/app/data/captures/capture_{int(__import__('time').time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "ok", "saved": fname}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Minimal API for selenium to post DOM snippets
@app.post("/api/dom")
async def save_dom(payload: Request):
    try:
        data = await payload.json()
        os.makedirs("/app/data/dom", exist_ok=True)
        fname = f"/app/data/dom/dom_{int(__import__('time').time())}.html"
        # If payload has 'dom' field save snippet, else store full JSON
        if isinstance(data, dict) and data.get("dom"):
            with open(fname, "w", encoding="utf-8") as f:
                f.write(data.get("dom")[:200000])  # limit size
        else:
            with open(fname + ".json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "ok", "saved": fname}
    except Exception as e:
        return {"error": str(e)}

# Start Selenium background thread (import here to avoid circular import on startup)
@app.on_event("startup")
async def startup_event():
    # Importing here so module file can be easily replaced
    try:
        from selenium_core import start_selenium_loop
        print("[main] Starting selenium thread...")
        start_selenium_loop()
    except Exception as e:
        print("[main] Failed to start selenium thread:", e)
