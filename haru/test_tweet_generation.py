import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
import json
import os
import requests
import http.client
import time
from google import genai

from activities.activity_post_a_tweet import PostTweetActivity
from framework.shared_data import SharedData
from skills.skill_chat import chat_skill
from skills.skill_generate_image import ImageGenerationSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tweet_generation():
    # Initialize shared data
    shared_data = SharedData()
    shared_data.initialize()  # Add initialization call
    
    # Load character config
    config_path = Path("config/character_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            character_config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Could not find character config at {config_path}")
        return
    
    # Add character config to shared data
    shared_data.update("system", {"character_config": character_config})
    
    # Create PostTweetActivity instance
    activity = PostTweetActivity()
    
    # Get personality data and build prompt
    personality_data = character_config.get("personality", {})
    recent_tweets = []  # Empty for testing, or you can add some sample tweets
    
    # Build the prompt
    prompt = activity._build_chat_prompt(personality_data, recent_tweets, shared_data)
    
    # Print the prompt for inspection
    print("\n=== Generated Prompt ===")
    print(prompt)
    print("\n=== End Prompt ===\n")
    
    # Generate tweet using Google AI
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("Google API key not found")
        return

    client = genai.Client(api_key=google_api_key)
    response = client.models.generate_content(
        model="gemini-exp-1206",
        contents=[prompt]
    )

    tweet_text = response.text.strip()
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    print("\n=== Generated Tweet ===")
    print(tweet_text)
    print(f"Length: {len(tweet_text)} characters")
    print("=== End Tweet ===\n")

    # Generate image for the tweet using Midjourney API
    print("\n=== Generating Image with Midjourney API ===")
    image_prompt, media_urls = await generate_image_with_midjourney(tweet_text, personality_data, shared_data, activity)
    
    if image_prompt:
        print("\n=== Generated Image Prompt ===")
        print(f"Image prompt: {image_prompt}")
        print("=== End Image Prompt ===\n")
    
    if media_urls and len(media_urls) > 0:
        print("\n=== Generated Image URL ===")
        print(media_urls[0])
        print("=== End Image URL ===\n")
    else:
        print("Image generation failed or not available.")

async def generate_image_with_midjourney(tweet_text, personality_data, shared_data, activity):
    """
    Generate an image using the Midjourney API via ImagineAPI.
    This is a standalone version of the _generate_image_for_tweet_mj method from PostTweetActivity.
    """
    logger.info("Starting image generation with ImagineAPI (Midjourney)")
    
    # Get the API key from environment variables
    mj_api_key = os.getenv("MJ_API_KEY")
    if not mj_api_key:
        logger.error("Midjourney API key not found in environment variables")
        return None, []
    
    # Extract origin from character config
    character_config = activity._get_character_config(shared_data)
    origin = character_config.get("backstory", {}).get("origin", "")
    
    # Generate a dynamic image prompt using Google AI
    image_prompt = await activity._generate_image_prompt(tweet_text, personality_data, origin)
    
    # Prepare the request data and headers
    data = {
        "prompt": image_prompt
    }
    
    headers = {
        'Authorization': f'Bearer {mj_api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Send the initial request to generate the image
        prompt_response = send_mj_request('POST', '/items/images/', data, headers)
        
        if not prompt_response.get('data', {}).get('id'):
            logger.error(f"Failed to initiate image generation: {prompt_response}")
            return image_prompt, []
        
        image_id = prompt_response['data']['id']
        logger.info(f"Image generation initiated with ID: {image_id}")
        
        # Poll for image completion
        start_time = time.time()
        completed_data = None
        max_wait_time = 300  # 5 minutes
        
        while time.time() - start_time < max_wait_time:
            completed_data = check_image_status(image_id, headers)
            if completed_data:
                break
            await asyncio.sleep(5)  # Wait for 5 seconds before checking again
        
        if not completed_data:
            logger.warning(f"Image generation timed out after {max_wait_time} seconds")
            return image_prompt, []
        
        if completed_data.get('status') == 'failed':
            logger.error(f"Image generation failed: {completed_data.get('error')}")
            return image_prompt, []
        
        # Get the image URL
        image_url = completed_data.get('url')

        # If upscaled versions are available, use the first one (they're typically higher quality)
        upscaled_urls = completed_data.get('upscaled_urls', [])
        if upscaled_urls and len(upscaled_urls) > 0:
            logger.info(f"Using upscaled image (1 of {len(upscaled_urls)} available)")
            image_url = upscaled_urls[0]
        
        if not image_url:
            logger.error("No image URL found in the completed data")
            return image_prompt, []
        
        logger.info(f"Successfully generated image: {image_url}")
        return image_prompt, [image_url]
        
    except Exception as e:
        logger.error(f"Error during image generation: {str(e)}")
        return image_prompt, []

def send_mj_request(method, path, body=None, headers=None):
    """Send a request to the ImagineAPI (Midjourney) service."""
    conn = http.client.HTTPSConnection("cl.imagineapi.dev")
    conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
    response = conn.getresponse()
    data = json.loads(response.read().decode())
    conn.close()
    return data

def check_image_status(image_id, headers):
    """Check the status of an image generation request."""
    response_data = send_mj_request('GET', f"/items/images/{image_id}", headers=headers)
    if response_data.get('data', {}).get('status') in ['completed', 'failed']:
        logger.info(f"Image generation completed with status: {response_data.get('data', {}).get('status')}")
        return response_data.get('data')
    else:
        logger.info(f"Image is still generating. Status: {response_data.get('data', {}).get('status')}")
        return None

if __name__ == "__main__":
    asyncio.run(test_tweet_generation()) 