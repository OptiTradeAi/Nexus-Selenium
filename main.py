from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os

from selenium_core import start_selenium_thread

app = FastAPI()

LOGIN_URL = "https://www.homebroker.com/pt/sign-in"


@app.get("/")
def root():
    return RedirectResponse(LOGIN_URL)


@app.on_event("startup")
def startup_event():
    print("[main] Starting selenium thread...")
    start_selenium_thread()


@app.get("/ping")
def ping():
    return {"status": "online", "service": "nexus-selenium-stpi"}
