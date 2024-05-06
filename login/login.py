# login/login.py
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import httpx
import logging
from logging_utils import setup_logging

setup_logging()

def get_cookies_using_selenium(grid_url='http://api.fulled.com.br:4444/wd/hub'):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Remote(
            command_executor=grid_url,
            options=chrome_options
        )
        with open('credentials/secrets.json') as f:
            secrets = json.load(f)

        driver.get(secrets["CBSNOOPER_LOGIN_URL"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys(secrets["CBSNOOPER_EMAIL"])
        driver.find_element(By.ID, "password").send_keys(secrets["CBSNOOPER_PASSWORD"])
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(lambda x: "dashboard" in driver.current_url)
        logging.info("Login bem-sucedido!")

        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        return cookies
    except Exception as e:
        logging.error(f"Erro ao logar: {str(e)}")
        return {}
    finally:
        driver.quit()

async def async_login_to_cbsnooper_and_transfer_session():
    cookies = get_cookies_using_selenium()
    if not cookies:
        logging.error("Falha ao obter cookies, verifique as credenciais e a conectividade.")
        return None
    client = httpx.AsyncClient(cookies=cookies)
    return client