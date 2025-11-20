import undetected_chromedriver as uc

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Descomente a linha abaixo para rodar em modo headless, se desejar
    # options.add_argument("--headless=new")

    driver = uc.Chrome(options=options)
    return driver
