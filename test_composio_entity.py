import os
from dotenv import load_dotenv
from pathlib import Path
from composio_openai import ComposioToolSet

# Load the .env file
env_path = Path("my_digital_being/.env")
load_dotenv(env_path)

api_key = os.environ.get("COMPOSIO_API_KEY")
twitter_username = os.environ.get("TWITTER_USERNAME")

if not api_key:
    print("No API key found!")
    exit(1)

if not twitter_username:
    print("No TWITTER_USERNAME found in environment!")
    exit(1)

print("Testing Composio entity creation...")

try:
    # First try without entity_id
    print("Attempting to create ComposioToolSet without entity_id...")
    toolset = ComposioToolSet(api_key=api_key)
    print("Success! Created toolset without entity_id")
except Exception as e:
    print(f"Failed without entity_id: {e}")
    
    try:
        # Try with entity_id
        print("\nAttempting to create ComposioToolSet with entity_id...")
        toolset = ComposioToolSet(
            api_key=api_key,
            entity_id=twitter_username,
            create_entity=True
        )
        print("Success! Created toolset with entity_id")
    except Exception as e:
        print(f"Failed with entity_id: {e}")
        exit(1)

# Try to get some tools to verify it's working
print("\nTesting tools access...")
try:
    tools = toolset.get_tools(actions=["COMPOSIO_LIST_APPS"])
    print("Successfully retrieved tools!")
except Exception as e:
    print(f"Error getting tools: {e}") 