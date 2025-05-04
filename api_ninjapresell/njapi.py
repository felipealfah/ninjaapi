from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import base64
import io
import logging
import re

# Configurando o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL do Selenium Hub
SELENIUM_HUB_URL = 'http://api.fulled.com.br:4444'

def validar_url(url):
    """ Verifica se a URL fornecida é válida. """
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (opcional)
        r'(www\.)?'  # www. (opcional)
        r'([a-zA-Z0-9.-]+)'  # Nome do domínio
        r'(\.[a-zA-Z]{2,6})'  # Extensão do domínio (como .com, .org, etc.)
        r'(:\d+)?'  # Porta (opcional)
        r'(\/.*)?$',  # Caminho opcional
        re.IGNORECASE
    )
    return re.match(regex, url) is not None

def adicionar_protocolo(url):
    """ Adiciona http:// como protocolo padrão se nenhum protocolo for encontrado na URL. """
    if not re.match(r'^(http://|https://)', url):
        logging.info(f"Protocolo não encontrado na URL, adicionando 'http://'.")
        return f"http://{url}"
    return url

def capturar_screenshot(url, largura, altura):
    """ Captura uma screenshot do URL especificado com a largura e altura fornecidas. """
    try:
        if not validar_url(url):
            raise ValueError(f"URL inválida: {url}")

        # Adiciona protocolo se necessário
        url = adicionar_protocolo(url)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        logging.info(f"Conectando ao Selenium Hub: {SELENIUM_HUB_URL}")
        driver = webdriver.Remote(
            command_executor=SELENIUM_HUB_URL,
            options=options
        )

        logging.info(f"Capturando screenshot de: {url} com largura={largura} e altura={altura}")
        driver.set_window_size(largura, altura)
        driver.get(url)
        screenshot = driver.get_screenshot_as_png()
        driver.quit()
        return screenshot

    except ValueError as ve:
        logging.error(f"Erro de validação: {ve}")
        raise
    except Exception as e:
        logging.error(f"Erro ao capturar screenshot: {e}")
        raise

def converter_base64(imagem_dados):
    """ Converte uma imagem de bytes para base64. """
    try:
        imagem = Image.open(io.BytesIO(imagem_dados))
        buffer = io.BytesIO()
        imagem.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logging.error(f"Erro ao converter imagem para base64: {e}")
        raise

def get_screenshots(url):
    """ Captura screenshots para versões desktop e mobile de um URL fornecido. """
    try:
        logging.info(f"Processando URL: {url}")
        
        # Captura screenshots nas dimensões desktop e mobile
        screenshot_desktop = capturar_screenshot(url, 1920, 1080)
        screenshot_mobile = capturar_screenshot(url, 375, 667)

        resposta = {
            'desktopImage': converter_base64(screenshot_desktop),
            'mobileImage': converter_base64(screenshot_mobile)
        }
        logging.info("Screenshots capturadas com sucesso.")
        return resposta

    except ValueError as ve:
        logging.error(f"Erro no processamento da URL: {ve}")
        raise ValueError(f"Erro no processamento da URL: {ve}")
    except Exception as e:
        logging.error(f"Erro geral ao processar screenshots: {e}")
        raise Exception(f"Erro geral ao processar screenshots: {e}")
