import subprocess
import sys
import os

def run_script(script_path):
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print(f"Execução de {script_path} concluída com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_path}: {e}")
        sys.exit(1)

def main():
    # Caminhos para os scripts
    scrape_url_script = os.path.join('etl', 'extracao', 'semanal', 'scrape_url.py')
    trans_url_final_script = os.path.join('etl', 'trans_insert', 'semanal', 'trans_url_final.py')
    insert_url_final_script = os.path.join('etl', 'trans_insert', 'semanal', 'insert_url_final.py')
    trans_trafego_script = os.path.join('etl', 'trans_insert', 'quinzenal', 'trans_trafego.py')
    insert_trafego_script = os.path.join('etl', 'trans_insert', 'quinzenal', 'insert_trafego.py')

    # Executar os scripts em sequência
    run_script(scrape_url_script)
    run_script(trans_url_final_script)
    run_script(insert_url_final_script)
    run_script(trans_trafego_script)
    run_script(insert_trafego_script)

if __name__ == "__main__":
    main()
