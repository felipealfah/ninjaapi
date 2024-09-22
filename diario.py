import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

def run_script(script_path):
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"Execution of {script_path} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")
        sys.exit(1)

def main():
    # Absolute paths to the scripts
    extracao_script = '/ninja/etl/extracao/diario/cb_scrape.py'
    trans_insert_script = '/ninja/etl/trans_insert/diario/trans_cb_diario.py'
    api_diario = '/ninja/etl/view/view_cb.py'

    # Execute the extraction script
    logging.info("Iniciando Extracao CB_scrapy")
    run_script(extracao_script)

    logging.info("Finalizando Extracao CB_scrapy")

    # Execute the insertion/transition script
    logging.info("Iniciando Atualização no Banco")
    run_script(trans_insert_script)

    logging.info("Finalizando Atualização")

    # Execute the script for exporting the data to the API
    logging.info("Criando API")
    run_script(api_diario)

    logging.info("Api criada e atualizada")

if __name__ == "__main__":
    main()
