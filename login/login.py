# login/login.py
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import httpx

def get_cookies_using_selenium(grid_url='http://selenium-hub:4444/wd/hub'):
    # Configuração das opções do navegador Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Criando a conexão com o Selenium Grid usando as opções configuradas
    driver = webdriver.Remote(
        command_executor=grid_url,
        options=chrome_options  # Aqui usamos 'options' ao invés de 'desired_capabilities'
    )

    # Certifique-se de que 'credentials/secrets.json' contém as credenciais necessárias
    with open('credentials/secrets.json') as f:
        secrets = json.load(f)

    try:
        driver.get(secrets["CBSNOOPER_LOGIN_URL"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys(secrets["CBSNOOPER_EMAIL"])
        driver.find_element(By.ID, "password").send_keys(secrets["CBSNOOPER_PASSWORD"])
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(lambda x: "dashboard" in driver.current_url)
        print("Login bem-sucedido!")

        # Coletar os cookies após o login e prepará-los para o httpx
        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    finally:
        driver.quit()  # Fechar a sessão do navegador

    return cookies

async def async_login_to_cbsnooper_and_transfer_session():
    cookies = get_cookies_using_selenium()
    client = httpx.AsyncClient(cookies=cookies)
    return client