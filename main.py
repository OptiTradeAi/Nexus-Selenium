# main.py
import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import json
import time

# tenta importar selenium_core do mesmo diretório; se não existir, o app ainda funciona
try:
    from selenium_core import selenium_core  # objeto ou módulo com start/open/get_source
    SEL_PRESENT = True
except Exception as e:
    selenium_core = None
    SEL_PRESENT = False
    print("[main] selenium_core não encontrado ou falha ao importar:", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # inicia selenium (se disponível) em thread daemon para não bloquear a API
    if SEL_PRESENT and hasattr(selenium_core, "start"):
        t = threading.Thread(target=selenium_core.start, daemon=True)
        t.start()
        # aguarda um pequeno tempo para permitir inicialização sem bloquear
        time.sleep(0.5)
    yield
    # on shutdown: tente fechar o driver
    try:
        if SEL_PRESENT and hasattr(selenium_core, "driver") and selenium_core.driver:
            try:
                selenium_core.driver.quit()
            except Exception:
                pass
    except Exception:
        pass

app = FastAPI(title="Nexus-Selenium", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def root():
    ok = {"status": "online", "selenium_available": bool(SEL_PRESENT)}
    return JSONResponse(content=ok)


@app.get("/injector", response_class=HTMLResponse)
def injector():
    # página simples que instrui o usuário a rodar o bookmarklet (bookmarklet faz o resto)
    html = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Nexus Injector</title></head>
      <body>
        <h3>Nexus Injector (HomeBroker)</h3>
        <p>Use o bookmarklet no navegador da HomeBroker. Após usar, verifique /selectors.</p>
        <p>Endpoints úteis:</p>
        <ul>
          <li>/open — pede para o Selenium abrir a HomeBroker (se estiver disponível)</li>
          <li>/source — retorna o último DOM capturado (se Selenium em execução)</li>
          <li>/selectors — mostra selectors salvos via bookmarklet</li>
        </ul>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/open")
def open_home():
    if not SEL_PRESENT or not hasattr(selenium_core, "open"):
        raise HTTPException(status_code=404, detail="Selenium não disponível")
    res = selenium_core.open(os.getenv("HB_URL", "https://www.homebroker.com/pt/sign-in"))
    return {"detail": res}


@app.get("/source")
def get_source():
    if not SEL_PRESENT or not hasattr(selenium_core, "get_source"):
        raise HTTPException(status_code=404, detail="Selenium não disponível")
    dom = selenium_core.get_source()
    if not dom:
        return JSONResponse(status_code=204, content={"detail": "Sem DOM ainda"})
    return HTMLResponse(content=dom)


# endpoint que o bookmarklet usa para enviar selectors/dom snapshots
@app.post("/capture")
async def capture(request: Request):
    token_header = request.headers.get("X-Nexus-Token") or request.query_params.get("token")
    expected = os.getenv("NEXUS_CAPTURE_SECRET")
    if expected and token_header != expected:
        raise HTTPException(status_code=403, detail="Invalid token")
    payload = await request.json()
    os.makedirs("data", exist_ok=True)
    ts = int(time.time())
    path = f"data/selectors_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # opcional: sobrescrever selectors.json (mais prático para selenium_core ler)
    try:
        with open("data/selectors.json", "w", encoding="utf-8") as f2:
            json.dump(payload, f2, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return {"detail": "saved", "path": path}


@app.get("/selectors")
def selectors_list():
    p = "data/selectors.json"
    if not os.path.exists(p):
        return JSONResponse(status_code=404, content={"detail": "selectors.json not found"})
    with open(p, "r", encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


# safe startup log so Render shows activity
@app.on_event("startup")
def startup_event():
    print("[main] Nexus-Selenium API started. Selenium present:", SEL_PRESENT)
