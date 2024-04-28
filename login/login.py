from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

def login_to_cbsnooper_and_transfer_session(headless=True, grid_url = 'http://api.fulled.com.br:4444/wd/hub'):
    with open('credentials/secrets.json') as f:
        secrets = json.load(f)

    options = Options()
    if headless:
        options.add_argument("--headless")  # Roda em modo headless
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-gpu")  # Desativa o GPU
        options.add_argument("--disable-dev-shm-usage")  # Supera limitações de recursos
        options.add_argument("--remote-debugging-port=9222")
    
    # Configuração para conectar ao Selenium Grid
    options.set_capability("browserName", "chrome")

    browser = webdriver.Remote(
        command_executor=grid_url,
        options=options  # Utiliza 'options' ao invés de 'desired_capabilities'
    )

    try:
        browser.get(secrets["CBSNOOPER_LOGIN_URL"])
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "email")))
        browser.find_element(By.ID, "email").send_keys(secrets["CBSNOOPER_EMAIL"])
        password_field = browser.find_element(By.ID, "password")
        password_field.send_keys(secrets["CBSNOOPER_PASSWORD"])
        password_field.send_keys(Keys.RETURN)

        WebDriverWait(browser, 10).until(lambda browser: "dashboard" in browser.current_url)
        print("Login bem-sucedido!")

        session = requests.Session()
        for cookie in browser.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        
        return session
    except Exception as e:
        print(f"Erro durante o login: {e}")
        return None
    finally:
        browser.quit()

#v1.2