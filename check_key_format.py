import os
from pathlib import Path
from dotenv import load_dotenv

def mask_api_key(key):
    if not key:
        return "None"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"

# Try to load .env from multiple possible locations
env_paths = [
    Path("my_digital_being/.env"),
    Path(".env"),
    Path("../.env")
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        print(f"Found .env file at: {env_path}")
        load_dotenv(env_path)
        env_loaded = True
        break

if not env_loaded:
    print("No .env file found!")

api_key = os.environ.get("COMPOSIO_API_KEY")
print(f"API Key found in environment: {mask_api_key(api_key)}")

# Check if it matches expected format (typically starts with 'co_' for Composio)
if api_key:
    if not api_key.startswith("co_"):
        print("Warning: Composio API keys typically start with 'co_'")
    
    # Check for common issues
    if api_key.startswith('"') or api_key.endswith('"'):
        print("Warning: API key contains quotes - these should be removed")
    if api_key.startswith("'") or api_key.endswith("'"):
        print("Warning: API key contains single quotes - these should be removed")
    if api_key.startswith(" ") or api_key.endswith(" "):
        print("Warning: API key contains leading/trailing whitespace - this should be removed")
    
    print(f"Key length: {len(api_key)} characters") 