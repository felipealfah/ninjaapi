import subprocess
import sys
import os

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

    # Execute the extraction script
    run_script(extracao_script)

    # Execute the insertion/transition script
    run_script(trans_insert_script)

if __name__ == "__main__":
    main()
