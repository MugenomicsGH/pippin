import os
from pathlib import Path
from dotenv import load_dotenv

def mask_string(s):
    if not s:
        return "None"
    if len(s) <= 8:
        return "***"
    return f"{s[:4]}...{s[-4:]}"

print("Current working directory:", os.getcwd())
print("Script location:", Path(__file__).absolute())

# Try to load .env from the script's directory
env_path = Path(__file__).parent / ".env"
print(f"\nLooking for .env at: {env_path}")
if env_path.exists():
    print("Found .env file")
    load_dotenv(env_path)
else:
    print("No .env file found at this location")

# Check environment variable
api_key = os.environ.get("COMPOSIO_API_KEY")
print(f"\nCOMPOSIO_API_KEY in environment: {mask_string(api_key)}")

# Try to read .env file directly
if env_path.exists():
    print("\nContents of .env file:")
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith("COMPOSIO_API_KEY"):
                key = line.split("=")[1].strip()
                print(f"COMPOSIO_API_KEY from file: {mask_string(key)}")
                break 