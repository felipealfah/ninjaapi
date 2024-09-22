from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import base64
import io

# URL do Selenium Hub
SELENIUM_HUB_URL = 'http://api.fulled.com.br:4444/wd/hub'

def capturar_screenshot(url, largura, altura):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Para desativar mensagens de log do navegador

    driver = webdriver.Remote(
        command_executor=SELENIUM_HUB_URL,
        options=options  # Atualizado para usar somente 'options'
    )

    driver.set_window_size(largura, altura)
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return screenshot

def converter_base64(imagem_dados):
    imagem = Image.open(io.BytesIO(imagem_dados))
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_screenshots(url):
    screenshot_desktop = capturar_screenshot(url, 1920, 1080)
    screenshot_mobile = capturar_screenshot(url, 375, 667)
    
    resposta = {
        'desktopImage': converter_base64(screenshot_desktop),
        'mobileImage': converter_base64(screenshot_mobile)
    }
    return resposta
