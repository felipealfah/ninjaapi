import requests
import json
import time

def login_to_cbsnooper_and_transfer_session():
    # Carrega as credenciais de um arquivo JSON
    with open('credentials/secrets.json') as f:
        secrets = json.load(f)
    
    login_url = secrets["CBSNOOPER_LOGIN_URL"]
    email = secrets["CBSNOOPER_EMAIL"]
    password = secrets["CBSNOOPER_PASSWORD"]

    # Dados do formulário de login
    login_data = {
        'email': email,
        'password': password
    }

    # Realiza o login usando uma sessão do requests
    session = requests.Session()
    response = session.post(login_url, data=login_data)

    # Verifica se o login foi bem-sucedido
    if response.status_code != 200 or "dashboard" not in response.url:
        print("Erro durante o login.")
        return None
    
    print("Login bem-sucedido!")

    # Retorna a sessão do requests
    return session
