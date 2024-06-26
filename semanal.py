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
    scrape_url_script = '/ninja/etl/extracao/semanal/scrape_url.py'
    trans_url_final_script = '/ninja/etl/trans_insert/semanal/trans_url_final.py'
    insert_url_final_script = '/ninja/etl/trans_insert/semanal/insert_url_final.py'

    # Execute the scripts sequentially
    run_script(scrape_url_script)
    run_script(trans_url_final_script)
    run_script(insert_url_final_script)

if __name__ == "__main__":
    main()
