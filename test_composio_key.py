import os
from composio_openai import ComposioToolSet

api_key = os.environ.get("COMPOSIO_API_KEY")
print(f"Testing Composio API key...")
try:
    toolset = ComposioToolSet(api_key=api_key, entity_id="TestEntity")
    print("API key is valid!")
except Exception as e:
    print(f"API key validation failed: {str(e)}") 