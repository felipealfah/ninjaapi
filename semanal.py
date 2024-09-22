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
    scrape_url_script = '/ninja/etl/extracao/semanal/scrape_url.py'
    trans_url_final_script = '/ninja/etl/trans_insert/semanal/trans_url_final.py'
    insert_url_final_script = '/ninja/etl/trans_insert/semanal/insert_url_final.py'
    bg_scrape = '/ninja/etl/extracao/semanal/bg_scrape.py'
    insert_bg_scrape = '/ninja/etl/trans_insert/semanal/bg_semanal.py'
    trans_cb_semanal = '/ninja/etl/trans_insert/semanal/trans_cb_semanal.py'
    scrape_url_cb_semanal='/ninja/etl/extracao/semanal/cb_semanal.py'


    # Execute the scripts sequentially
    logging.info("Iniciando Buy Googds Scrapy")
    run_script(bg_scrape)
    logging.info("Atualizando Buy Goods no Banco")
    run_script(insert_bg_scrape)
    logging.info("Iniciando Scrapy de url")
    run_script(scrape_url_script)
    logging.info("Atualizando URL")
    run_script(trans_url_final_script)
    logging.info("Atualizando url no banco")
    run_script(insert_url_final_script)
    logging.info("Iniciando Scrapy de url clickbank")
    run_script(scrape_url_cb_semanal)
    logging.info("Atualizando o Banco")
    run_script(trans_cb_semanal)

if __name__ == "__main__":
    main()
