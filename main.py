from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
import os
from dotenv import load_dotenv
import agent

load_dotenv()

app = FastAPI(title="Nexus-Selenium API")

@app.get("/")
def root():
    return {"status": "ok", "detail": "Nexus Selenium service. Use /start_scan or /status"}

@app.get("/start_scan")
def start_scan(background: bool = True):
    """
    Trigger a selenium discovery/login attempt.
    If AUTO_LOGIN true and credentials exist, will try to login.
    """
    res = agent.start_agent(background=background)
    return JSONResponse(content=res)

@app.get("/status")
def status():
    return JSONResponse(content=agent.get_status())

@app.get("/start_scan_and_redirect")
def start_and_redirect():
    """
    For convenience: opens the HomeBroker sign-in in the browser (useful for manual assisted flow).
    This endpoint simply returns a redirect to the start URL (client/browser should follow).
    """
    start_url = os.getenv("START_URL", "https://www.homebroker.com/pt/sign-in")
    return RedirectResponse(url=start_url)
