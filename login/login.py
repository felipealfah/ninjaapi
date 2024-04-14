# login.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time

def login_to_cbsnooper_and_transfer_session(headless=True):
    # Carrega as credenciais de um arquivo JSON
    with open('credentials/secrets.json') as f:
        secrets = json.load(f)
    
    # Configurações do WebDriver
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Inicializa o WebDriver
    browser = webdriver.Chrome(options=options)
    browser.get(secrets["CBSNOOPER_LOGIN_URL"])

    # Aguarda até que o campo de e-mail esteja disponível e realiza o login
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "email")))
    browser.find_element(By.ID, "email").send_keys(secrets["CBSNOOPER_EMAIL"])
    password_field = browser.find_element(By.ID, "password")
    password_field.send_keys(secrets["CBSNOOPER_PASSWORD"])
    password_field.send_keys(Keys.RETURN)
    
    # Aguarda um tempo para o login ser processado
    time.sleep(5)
    
    # Verifica se o login foi bem-sucedido
    if "dashboard" not in browser.current_url:
        print("Erro durante o login.")
        browser.quit()
        return None
    
    print("Login bem-sucedido!")

    # Inicializa uma sessão do requests e transfere os cookies
    session = requests.Session()
    for cookie in browser.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    # Fecha o navegador
    browser.quit()
    
    # Retorna a sessão do requests
    return session
