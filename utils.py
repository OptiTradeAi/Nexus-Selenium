import os

def save_screenshot(driver, filename):
    path = os.path.join("/app", filename)
    driver.save_screenshot(path)
    print(f"[Screenshot] Salvo em {path}")
