from fastapi import FastAPI, Request, Header
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from threading import Thread
import time

# token para validar origem
BACKEND_TOKEN = os.getenv("TOKEN", "032318")

app = FastAPI()

# serve arquivos estáticos (loader, scanner etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

# endpoints simples
@app.get("/")
def root():
    # redireciona para a HomeBroker login
    return RedirectResponse("https://www.homebroker.com/pt/sign-in")

@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}

# endpoint que o scanner + selenium envia (dados de captura / eventos)
@app.post("/capture")
async def capture(req: Request, x_nexus_token: str | None = Header(None)):
    try:
        if x_nexus_token != BACKEND_TOKEN:
            return JSONResponse({"ok": False, "reason": "invalid token"}, status_code=403)
        payload = await req.json()
        # salva payload para debug
        ts = int(time.time())
        filename = f"/app/data/capture_{ts}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[/capture] Received payload: {payload.get('event','no-event')} url: [{payload.get('url')}]")
        return {"ok": True}
    except Exception as e:
        print("[/capture] error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# endpoint para salvar cookies (opcional — ativar apenas com consentimento)
@app.post("/save_cookies")
async def save_cookies(req: Request, x_nexus_token: str | None = Header(None)):
    try:
        if x_nexus_token != BACKEND_TOKEN:
            return JSONResponse({"ok": False, "reason": "invalid token"}, status_code=403)
        payload = await req.json()
        with open("/app/data/saved_cookies.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print("[/save_cookies] Cookies/localStorage saved.")
        return {"ok": True}
    except Exception as e:
        print("[/save_cookies] error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# API endpoint to accept DOM snippets saved by Selenium
@app.post("/api/dom")
async def api_dom(req: Request, x_nexus_token: str | None = Header(None)):
    try:
        if x_nexus_token != BACKEND_TOKEN:
            return JSONResponse({"ok": False, "reason": "invalid token"}, status_code=403)
        payload = await req.json()
        ts = int(time.time())
        snippet = payload.get("dom_snippet", "")[:4000]
        meta = {
            "url": payload.get("current_url"),
            "timestamp": payload.get("timestamp", ts)
        }
        filename = f"/app/data/dom_snippet_{ts}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(snippet)
        print(f"[/api/dom] DOM saved snippet from [{meta['url']}]")
        return {"ok": True}
    except Exception as e:
        print("[/api/dom] error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


# start selenium in background
def start_selenium_thread():
    try:
        from selenium_core import start_selenium_loop
        start_selenium_loop()
    except Exception as e:
        print("[main] Error starting selenium loop:", e)

@app.on_event("startup")
async def startup_event():
    print("[main] Starting selenium thread...")
    t = Thread(target=start_selenium_thread, daemon=True)
    t.start()
