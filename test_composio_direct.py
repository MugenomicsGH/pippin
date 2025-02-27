import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load the .env file
env_path = Path("my_digital_being/.env")
load_dotenv(env_path)

api_key = os.environ.get("COMPOSIO_API_KEY")
if not api_key:
    print("No API key found!")
    exit(1)

# Try to make a direct API call to Composio
base_url = "https://backend.composio.dev/api/v2/actions/list/all"
headers = {"x-api-key": api_key}

try:
    print("Making API call to Composio...")
    response = requests.get(base_url, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! API key is valid.")
        data = response.json()
        print(f"Found {len(data.get('items', []))} actions")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error making API call: {e}") 