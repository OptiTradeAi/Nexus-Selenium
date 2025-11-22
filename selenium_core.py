import time
import json
import os
import undetected_chromedriver as uc

HOME_BROKER_URL = "https://www.homebroker.com/pt/invest"

class NexusSelenium:
    def __init__(self):
        self.driver = None

    def start(self):
        print("[nexus] iniciando chrome…")
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1280,720")

        self.driver = uc.Chrome(options=options)

        print("[nexus] abrindo corretora…")
        self.driver.get(HOME_BROKER_URL)
        time.sleep(8)

        print("[nexus] iniciando varredura…")
        scan_data = self.scan_page()

        print("[nexus] salvando dados…")
        self.save_scan(scan_data)

    def scan_page(self):
        data = {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "elements": []
        }

        elems = self.driver.find_elements("xpath", "//*")
        for e in elems:
            try:
                info = {
                    "tag": e.tag_name,
                    "type": e.get_attribute("type"),
                    "id": e.get_attribute("id"),
                    "name": e.get_attribute("name"),
                    "class": e.get_attribute("class"),
                    "text": e.text[:200]
                }
                data["elements"].append(info)
            except:
                pass

        return data

    def save_scan(self, data):
        os.makedirs("/app/data", exist_ok=True)
        with open("/app/data/scan.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("[nexus] scan salvo em /app/data/scan.json")
