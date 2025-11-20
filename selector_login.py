from selenium.webdriver.common.by import By

LOGIN_SELECTORS = {
    "email": (By.XPATH, "//input[@placeholder='Digite seu e-mail']"),
    "password": (By.XPATH, "//input[@placeholder='Digite sua senha']"),
    "button_login": (By.XPATH, "//button[contains(text(), 'Iniciar sessão')]")
}
