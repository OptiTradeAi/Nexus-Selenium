from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Token
BACKEND_TOKEN = os.getenv("TOKEN", "032318")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    # AUTO-REDIRECT → HomeBroker login
    return RedirectResponse("https://www.homebroker.com/pt/sign-in")


@app.get("/ping")
def ping():
    return {"status": "online", "token": BACKEND_TOKEN}
