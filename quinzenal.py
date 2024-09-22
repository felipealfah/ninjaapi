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
    trans_trafego_script = '/ninja/etl/trans_insert/quinzenal/trans_trafego.py'
    insert_trafego_script = '/ninja/etl/trans_insert/quinzenal/insert_trafego.py'

    # Execute the scripts sequentially
    logging.info("Iniciando Busca do Trafego")
    run_script(trans_trafego_script)
    logging.info("Atualizando informações do trafego no Banco")
    run_script(insert_trafego_script)

if __name__ == "__main__":
    main()
