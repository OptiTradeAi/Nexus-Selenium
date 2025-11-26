from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import threading

# Import start function from selenium_core
from selenium_core import start_selenium_loop, is_selenium_running

app = FastAPI()

# Token (env default)
BACKEND_TOKEN = os.getenv("TOKEN", "032318")
NEXUS_PUBLIC_URL = os.getenv("NEXUS_PUBLIC_URL", f"https://{os.getenv('RENDER_SERVICE_NAME','nexus-selenium.onrender.com')}")
NEXUS_TOKEN = os.getenv("NEXUS_TOKEN", BACKEND_TOKEN)

# mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    # redirect user to homebroker sign-in (this is the clickable link idea)
    return RedirectResponse("https://www.homebroker.com/pt/sign-in")

@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN, "selenium_running": is_selenium_running()}

# capture endpoint receives scanner payloads
@app.post("/capture")
async def capture(request: Request, x_nexus_token: str | None = Header(None)):
    if x_nexus_token != NEXUS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    payload = await request.json()
    # Save for debugging
    try:
        ts = payload.get("timestamp") or payload.get("time") or None
        fname = f"/app/data/capture_{int(__import__('time').time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            import json
            json.dump({"received": payload}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving capture:", e)
    print("[/capture] Received payload:", payload.get("event", "no-event"), "url:", payload.get("url") or payload.get("current_url"))
    return JSONResponse({"status": "captured"})

# optional endpoint to receive DOM posts from selenium if needed
@app.post("/api/dom")
async def api_dom(request: Request, x_nexus_token: str | None = Header(None)):
    if x_nexus_token != NEXUS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    payload = await request.json()
    try:
        with open("/app/data/last_dom.html", "w", encoding="utf-8") as f:
            f.write(payload.get("dom", "")[:200000])  # keep snippet
    except Exception as e:
        print("Error saving dom:", e)
    print("[/api/dom] DOM saved snippet from", payload.get("current_url"))
    return {"status": "ok"}

# start selenium loop on startup
@app.on_event("startup")
async def startup_event():
    print("[main] Startup event: starting selenium loop thread")
    start_selenium_loop()
