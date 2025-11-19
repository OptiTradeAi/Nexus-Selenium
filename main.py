from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import os

app = FastAPI()

SCAN_FILE = "/app/homebroker_xpath_scan.json"

def scan_login_fields():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get("https://www.homebroker.com/pt/sign-in")
    time.sleep(5)

    results = {
        "inputs": [],
        "buttons": [],
        "all_elements": []
    }

    elements = driver.find_elements(By.XPATH, "//*")

    for el in elements:
        try:
            tag = el.tag_name
            elem = {
                "tag": tag,
                "text": el.text,
                "id": el.get_attribute("id"),
                "name": el.get_attribute("name"),
                "type": el.get_attribute("type"),
                "class": el.get_attribute("class"),
                "placeholder": el.get_attribute("placeholder"),
                "xpath": "",
            }

            # gerar xpath absoluto
            path = driver.execute_script("""
                function absoluteXPath(element) {
                    if (element === document.body)
                        return '/html/body';
                    var ix= 0;
                    var siblings= element.parentNode.childNodes;
                    for (var i= 0; i<siblings.length; i++) {
                        var sibling= siblings[i];
                        if (sibling===element)
                            return absoluteXPath(element.parentNode)+'/'+element.tagName+'['+(ix+1)+']';
                        if (sibling.nodeType===1 && sibling.tagName===element.tagName)
                            ix++;
                    }
                }
                return absoluteXPath(arguments[0]);
            """, el)

            elem["xpath"] = path

            results["all_elements"].append(elem)

            if tag == "input":
                results["inputs"].append(elem)

            if tag == "button":
                results["buttons"].append(elem)

        except:
            continue

    driver.quit()

    # salvar JSON no servidor para download
    with open(SCAN_FILE, "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results


@app.get("/")
def root():
    return {"status": "XPath Scanner ON 🚀", "usage": "/scan para visualizar | /download para baixar"}


@app.get("/scan")
def scan():
    """Retorna o JSON completo na tela para copiar."""
    try:
        data = scan_login_fields()
        return JSONResponse(content=data)
    except Exception as e:
        return {"error": str(e)}


@app.get("/download")
def download():
    """Gera e faz download automático do JSON."""
    try:
        scan_login_fields()
        if os.path.exists(SCAN_FILE):
            return FileResponse(
                SCAN_FILE,
                media_type="application/json",
                filename="HomeBroker_XPath_Scan.json"
            )
        else:
            return {"error": "Arquivo não encontrado após o scan."}
    except Exception as e:
        return {"error": str(e)}
