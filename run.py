import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded .env file from: {env_file}")
else:
    print(f"Error: .env file not found at: {env_file}")

# Set PYTHONPATH
os.environ['PYTHONPATH'] = 'src'

# Run Uvicorn with reload
command = ['uvicorn', 'src.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running Uvicorn: {e}")
    raise