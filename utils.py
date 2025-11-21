import time
import base64
from selenium.webdriver.remote.webdriver import WebDriver

def take_screenshot(driver: WebDriver, path: str):
    driver.save_screenshot(path)

def sleep(t=0.2):
    time.sleep(t)
