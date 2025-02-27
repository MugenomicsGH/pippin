import os
from dotenv import load_dotenv
from pathlib import Path
from composio_openai import ComposioToolSet

# Load the .env file
env_path = Path("my_digital_being/.env")
load_dotenv(env_path)

api_key = os.environ.get("COMPOSIO_API_KEY")
if not api_key:
    print("No API key found!")
    exit(1)

print("Checking Composio connections...")
toolset = ComposioToolSet(api_key=api_key)

# Try to list available apps and their auth status
try:
    print("\nChecking Twitter integration status...")
    result = toolset.execute_action(
        action="COMPOSIO_LIST_APPS",
        params={}
    )
    
    if result.get("success") or result.get("successfull"):
        apps = result.get("data", {}).get("apps", [])
        for app in apps:
            if app.get("key", "").lower() == "twitter":
                print("\nTwitter app info:")
                print(f"  Name: {app.get('name')}")
                print(f"  Key: {app.get('key')}")
                print(f"  Status: {app.get('status')}")
                print(f"  Auth Required: {app.get('authRequired')}")
                break
    else:
        print("Failed to list apps:", result.get("error"))
except Exception as e:
    print(f"Error checking Twitter status: {e}")

# Try to execute a simple Twitter action to test connection
try:
    print("\nTesting Twitter connection...")
    result = toolset.execute_action(
        action="TWITTER_GET_USER_BY_USERNAME",
        params={"username": "RedBeanWay"},
        entity_id="MyDigitalBeing"
    )
    print("Connection test result:", result)
except Exception as e:
    print(f"Error testing Twitter connection: {e}") 