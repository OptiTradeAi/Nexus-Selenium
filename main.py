from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time
import json
from pathlib import Path
from typing import Optional

# inicia app
app = FastAPI()

# config / paths
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CAPTURE_FILE = DATA_DIR / "captures.log"        # appenda JSON lines
DOM_DIR = DATA_DIR / "dom"
DOM_DIR.mkdir(parents=True, exist_ok=True)

# token (env)
BACKEND_TOKEN = os.getenv("TOKEN", "032318")

# mount static (loader.js, scanner.js etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

# constants
LOGIN_REDIRECT = os.getenv("NEXUS_LOGIN_URL", "https://www.homebroker.com/pt/invest")
BACKEND_PUBLIC = os.getenv("BACKEND_PUBLIC_URL", None)  # optional


@app.get("/")
def root():
    """
    Redireciona (se quiser) para a página de login da corretora.
    Se preferir, você já pode usar /static/injector.html localmente.
    """
    return RedirectResponse(LOGIN_REDIRECT)


@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}


def _verify_token(x_token: Optional[str]):
    if BACKEND_TOKEN and x_token != BACKEND_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/capture")
async def capture(request: Request, x_nexus_token: Optional[str] = Header(None)):
    """
    Endpoint para receber capturas (scanner / selenium).
    Exige header X-Nexus-Token igual ao TOKEN do env (se definido).
    Salva em CAPTURE_FILE em formato JSON line (um JSON por linha).
    """
    try:
        _verify_token(x_nexus_token)
    except HTTPException as e:
        raise e

    payload = await request.json()
    # adiciona metadados
    payload["_received_at"] = time.time()
    # gravar como JSON line
    try:
        with open(CAPTURE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        return JSONResponse({"status": "error", "msg": f"write_failed: {e}"}, status_code=500)

    return {"status": "ok", "saved": True, "url": payload.get("url")}


@app.post("/api/dom")
async def api_dom(request: Request):
    """
    Endpoint simples para salvar snippets / DOM recebidos.
    Salva como arquivos DOM_TIMESTAMP.html para análise.
    (Não exige token for now so you can post quickly from selenium)
    """
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse({"status": "error", "msg": "invalid json"}, status_code=400)

    dom = data.get("dom") or data.get("dom_snippet") or ""
    url = data.get("url", "unknown")
    ts = int(time.time())
    filename = DOM_DIR / f"dom_{ts}.html"
    try:
        # salva apenas uma parte se for grande
        if len(dom) > 1_000_000:
            dom_to_save = dom[:1_000_000]
        else:
            dom_to_save = dom
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"<!-- url: {url} timestamp: {ts} -->\n")
            f.write(dom_to_save)
    except Exception as e:
        return JSONResponse({"status": "error", "msg": f"write_failed: {e}"}, status_code=500)

    return {"status": "ok", "file": str(filename.name)}


# Optional small helper to view last captures (for quick debugging)
@app.get("/captures/last")
def captures_last(n: int = 10):
    lines = []
    try:
        if CAPTURE_FILE.exists():
            with open(CAPTURE_FILE, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
            for l in all_lines[-n:]:
                try:
                    lines.append(json.loads(l))
                except:
                    lines.append({"raw": l})
    except Exception as e:
        return {"status": "error", "msg": str(e)}
    return {"status": "ok", "count": len(lines), "last": lines}


# ---- Selenium thread starter (importa somente se existir selenium_core)
try:
    from selenium_core import start_selenium_thread
except Exception as e:
    start_selenium_thread = None
    print("[main] selenium_core not importable at startup:", e)


@app.on_event("startup")
async def startup_event():
    # inicia selenium em background (se disponível)
    if callable(start_selenium_thread):
        print("[main] Starting selenium thread...")
        start_selenium_thread()
    else:
        print("[main] selenium thread not started (selenium_core not found).")


# run with uvicorn main:app --host 0.0.0.0 --port 10000
