from composio_openai import ComposioToolSet

print("Testing Composio API key with simple initialization...")
try:
    composio_toolset = ComposioToolSet(api_key="your_api_key_here")  # Replace this with your actual API key
    print("Successfully initialized ComposioToolSet!")
    
    # Try to get tools as a basic test
    tools = composio_toolset.get_tools(actions=["COMPOSIO_LIST_APPS"])
    print("Successfully retrieved tools!")
except Exception as e:
    print(f"Error: {str(e)}") 