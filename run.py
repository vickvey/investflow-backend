# run.py
import os
import subprocess

def run_uvicorn():
    # Set the PYTHONPATH environment variable and run the uvicorn command
    os.environ['PYTHONPATH'] = 'src'
    subprocess.run(['uvicorn', 'src.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'])

if __name__ == "__main__":
    run_uvicorn()
