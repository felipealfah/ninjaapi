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
    extracao_script = os.path.join('etl', 'extracao', 'diario', 'cb_scrape.py')
    trans_insert_script = os.path.join('etl', 'trans_insert', 'diario', 'trans_cb_diario.py')

    # Executar o script de extração
    run_script(extracao_script)

    # Executar o script de inserção/transição
    run_script(trans_insert_script)

if __name__ == "__main__":
    main()
