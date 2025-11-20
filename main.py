from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nexus_login import NexusLogin
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/login")
def do_login():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    nexus = NexusLogin(driver)

    result = nexus.try_login(
        email="SEU_EMAIL_AQUI",
        password="SUA_SENHA_AQUI"
    )

    driver.quit()
    return jsonify(result)

@app.route("/")
def home():
    return jsonify({"status": "Nexus Selenium Online 🚀"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
