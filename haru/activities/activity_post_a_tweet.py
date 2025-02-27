import logging
import os
import requests
import json
import time
import http.client
from typing import Dict, Any, List, Tuple
import re
import asyncio
import random

from framework.activity_decorator import activity, ActivityBase, ActivityResult
from framework.api_management import api_manager
from framework.memory import Memory
from skills.skill_chat import chat_skill
from skills.skill_generate_image import ImageGenerationSkill
from skills.skill_x_api import XAPISkill
from google import genai
from google.genai import Client

logger = logging.getLogger(__name__)

# Style references for different Japanese art styles
STYLE_REFS = [
    "851985277",  # Traditional Japanese woodblock print style
    "378114956",  # Ink wash painting style
]

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@activity(
    name="post_a_tweet",
    energy_cost=0.4,
    cooldown=3600,  # 1 hour
    required_skills=["twitter_posting", "image_generation"],
)
class PostTweetActivity(ActivityBase):
    """
    Uses Google AI to generate tweet text,
    referencing the character's personality from character_config.
    Checks recent tweets in memory to avoid duplication.
    Posts to Twitter via Composio's "Creation of a post" dynamic action.
    """

    def __init__(self):
        super().__init__()
        self.max_length = 280
        # If you know your Twitter username, you can embed it in the link
        # or fetch it dynamically. Otherwise, substitute accordingly:
        self.twitter_username = "RedBeanWay"
        # set this to True if you want to generate an image for the tweet
        self.image_generation_enabled = True
        self.default_size = (1024, 1024)  # Added for image generation
        self.default_format = "png"  # Added for image generation
        # Maximum time to wait for image generation (in seconds)
        self.max_wait_time = 300  # 5 minutes

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger.info("Starting tweet posting activity...")

            # 1) Gather personality + recent tweets
            character_config = self._get_character_config(shared_data)
            personality_data = character_config.get("personality", {})
            recent_tweets = self._get_recent_tweets(shared_data, limit=10)

            # 2) Generate tweet text with Google AI
            prompt_text = self._build_chat_prompt(personality_data, recent_tweets, shared_data)
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                return ActivityResult(success=False, error="Google API key not found")

            client = Client(api_key=google_api_key)
            response = client.models.generate_content(
                model="gemini-exp-1206",
                contents=[prompt_text]
            )

            tweet_text = response.text.strip()
            if len(tweet_text) > self.max_length:
                tweet_text = tweet_text[: self.max_length - 3] + "..."

            # 3) Generate an image based on the tweet text
            if self.image_generation_enabled:
                image_prompt, media_urls = await self._generate_image_for_tweet_mj(tweet_text, personality_data, shared_data)
            else:
                image_prompt, media_urls = None, []

            # 4) Post the tweet via X API
            x_api = XAPISkill({
                "enabled": True,
                "twitter_username": self.twitter_username
            })
            post_result = await x_api.post_tweet(tweet_text, media_urls)
            if not post_result["success"]:
                error_msg = post_result.get(
                    "error", "Unknown error posting tweet via Composio"
                )
                logger.error(f"Tweet posting failed: {error_msg}")
                return ActivityResult(success=False, error=error_msg)

            tweet_id = post_result.get("tweet_id")
            tweet_link = (
                f"https://twitter.com/{self.twitter_username}/status/{tweet_id}"
                if tweet_id
                else None
            )

            # 5) Return success, adding link & prompt in metadata
            logger.info(f"Successfully posted tweet: {tweet_text[:50]}...")
            return ActivityResult(
                success=True,
                data={"tweet_id": tweet_id, "content": tweet_text},
                metadata={
                    "length": len(tweet_text),
                    "method": "google_ai",
                    "model": "gemini-exp-1206",
                    "tweet_link": tweet_link,
                    "prompt_used": prompt_text,
                    "image_prompt_used": image_prompt,
                    "image_count": len(media_urls),
                },
            )

        except Exception as e:
            error_message = strip_html_tags(str(e))
            logger.error(f"Failed to post tweet: {error_message}", exc_info=True)
            return ActivityResult(success=False, error=error_message)

    def _get_character_config(self, shared_data) -> Dict[str, Any]:
        """
        Retrieve character_config from SharedData['system'] or re-init the Being if not found.
        """
        system_data = shared_data.get_category_data("system")
        maybe_config = system_data.get("character_config")
        if maybe_config:
            return maybe_config

        # fallback
        from framework.main import DigitalBeing

        being = DigitalBeing()
        being.initialize()
        return being.configs.get("character_config", {})

    def _get_recent_tweets(self, shared_data, limit: int = 10) -> List[str]:
        """
        Fetch the last N tweets posted (activity_type='PostTweetActivity') from memory.
        """
        system_data = shared_data.get_category_data("system")
        memory_obj: Memory = system_data.get("memory_ref")

        if not memory_obj:
            from framework.main import DigitalBeing

            being = DigitalBeing()
            being.initialize()
            memory_obj = being.memory

        recent_activities = memory_obj.get_recent_activities(limit=50, offset=0)
        tweets = []
        for act in recent_activities:
            if act.get("activity_type") == "PostTweetActivity" and act.get("success"):
                tweet_body = act.get("data", {}).get("content", "")
                if tweet_body:
                    tweets.append(tweet_body)

        return tweets[:limit]

    def _build_chat_prompt(self, personality: Dict[str, Any], recent_tweets: List[str], shared_data: Dict[str, Any]) -> str:
        """
        Construct the user prompt referencing personality + last tweets.
        """
        trait_lines = [f"{t}: {v}" for t, v in personality.items()]
        personality_str = "\n".join(trait_lines)

        if recent_tweets:
            last_tweets_str = "\n".join(f"- {txt}" for txt in recent_tweets)
        else:
            last_tweets_str = "(No recent tweets)"

        # Get backstory information from character config
        character_config = self._get_character_config(shared_data)
        backstory = character_config.get("backstory", {})
        origin = backstory.get("origin", "")
        purpose = backstory.get("purpose", "")
        core_values = backstory.get("core_values", [])
        example_posts = backstory.get("example_posts", [])
        writing_style = backstory.get("writing_style", "")
        instructions = backstory.get("instructions", "")
        core_values_str = ", ".join(core_values) if core_values else ""

        # Get a random favorite topic from preferences
        preferences = character_config.get("preferences", {})
        favorite_topics = preferences.get("favorite_topics", [])
        random_topic = random.choice(favorite_topics) if favorite_topics else "the way of the red bean"
        logger.info(f"Selected random topic for tweet: {random_topic}")

        return (
            f"{origin}\n"
            f"Writing Style: {writing_style}\n"
            f"Instructions: {instructions}\n"
            f"Here are your most recent tweets, for reference:\n"
            f"{last_tweets_str}\n\n"
            f"Here is a selection of example posts in your writing style:\n"
            f"{example_posts}\n\n"
            f"Your current mood is:\n"
            f"{personality_str}\n\n"
            f"Write a new short tweet (under 280 chars) that reflects your current mood and backstory. Today, you feel particularly drawn to muse about '{random_topic}'. Keep it interesting and creative. Write an inspirational quote, pose a riddle, write a haiku, make a completely nonsensical observation that sounds like a meme, or anything else that's interesting to you, but make sure the tweet is about the aforementioned topic. Stay in character.\n"
            f"IMPORTANT: DO NOT USE HASHTAGS OR EMOJIS.\n"
        )

    async def _generate_image_prompt(self, tweet_text: str, personality_data: Dict[str, Any], origin: str) -> str:
        """
        Use Google AI to generate a dynamic image prompt based on the tweet text.
        """
        logger.info("Generating dynamic image prompt with Google AI")
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning("Google API key not found, using fallback image prompt")
            return self._build_fallback_image_prompt(tweet_text, origin)
        
        # Create a prompt for the AI to generate an image prompt
        prompt_for_image_prompt = (
            f"I need you to create a prompt for Midjourney image generation AI based on this tweet: \"{tweet_text}\"\n\n"
            f"Do not use any midjourney parameters in your prompt, only describe the image you want to see."
            f"The image must contain a concise japanese phrase in katakana, so be sure to include that in your prompt like so: 'with the japanese phrase [insert phrase] in ink brush style beside the illustration'."
            f"Match the tone of the tweet and the origin story. If the tweet is humorous, the image and phrase should be humorous as well. If the tweet is serious, the image and phrase should be serious.\n\n"
            f"Return ONLY the prompt text with no additional explanation or commentary. Keep your prompt concise and interesting. 20 words or less. Do not include a sage old man in the prompt."
            f"Here is an example serious prompt: 'A cherry blossom tree in springtime with the phrase '春を待つ' in ink brush style beside the illustration'"
            f"Here is an example humorous prompt: 'Pepe the frog in a kimono with the phrase '良いカエル' in ink brush style beside the illustration'"
        )
        
        try:
            client = Client(api_key=google_api_key)
            response = client.models.generate_content(
                model="gemini-exp-1206",
                contents=[prompt_for_image_prompt]
            )
            
            image_prompt = response.text.strip()
            logger.info(f"Generated dynamic image prompt: {image_prompt}")
            
            # Randomly select two style references
            selected_styles = random.sample(STYLE_REFS, 2)
            style_params = " ".join(f"--sref {style}" for style in selected_styles)
            
            # Ensure the prompt includes Midjourney parameters
            if "--ar" not in image_prompt:
                image_prompt += f" --ar 1:1 {style_params}"
            
            logger.info(f"Final image prompt with style refs: {image_prompt}")
            return image_prompt
            
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            return self._build_fallback_image_prompt(tweet_text, origin)

    def _build_fallback_image_prompt(self, tweet_text: str, origin: str) -> str:
        """Fallback method for image prompt generation if AI generation fails."""
        # Randomly select two style references for fallback prompt
        selected_styles = random.sample(STYLE_REFS, 2)
        style_params = " ".join(f"--sref {style}" for style in selected_styles)
        return f"Traditional japanese print inspired by this phrase: {tweet_text} --ar 1:1 {style_params}"

    def _send_mj_request(self, method, path, body=None, headers=None):
        """Send a request to the ImagineAPI (Midjourney) service."""
        conn = http.client.HTTPSConnection("cl.imagineapi.dev")
        conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        return data

    def _check_image_status(self, image_id, headers):
        """Check the status of an image generation request."""
        response_data = self._send_mj_request('GET', f"/items/images/{image_id}", headers=headers)
        if response_data.get('data', {}).get('status') in ['completed', 'failed']:
            logger.info(f"Image generation completed with status: {response_data.get('data', {}).get('status')}")
            return response_data.get('data')
        else:
            logger.info(f"Image is still generating. Status: {response_data.get('data', {}).get('status')}")
            return None

    async def _generate_image_for_tweet_mj(self, tweet_text: str, personality_data: Dict[str, Any], shared_data: Dict[str, Any] = None) -> Tuple[str, List[str]]:
        """
        Generate an image for the tweet using ImagineAPI (Midjourney).
        Returns a tuple of (image_prompt, media_urls).
        If generation fails, returns (None, []).
        """
        logger.info("Starting image generation with ImagineAPI (Midjourney)")
        
        # Get the API key from environment variables
        mj_api_key = os.getenv("MJ_API_KEY")
        if not mj_api_key:
            logger.error("Midjourney API key not found in environment variables")
            return None, []
        
        # Extract origin from character config
        character_config = self._get_character_config(shared_data)
        origin = character_config.get("backstory", {}).get("origin", "")
        
        # Generate a dynamic image prompt using Google AI
        image_prompt = await self._generate_image_prompt(tweet_text, personality_data, origin)
        
        # Prepare the request data and headers
        data = {
            "prompt": image_prompt,
        }
        
        headers = {
            'Authorization': f'Bearer {mj_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Send the initial request to generate the image
            prompt_response = self._send_mj_request('POST', '/items/images/', data, headers)
            
            if not prompt_response.get('data', {}).get('id'):
                logger.error(f"Failed to initiate image generation: {prompt_response}")
                return image_prompt, []
            
            image_id = prompt_response['data']['id']
            logger.info(f"Image generation initiated with ID: {image_id}")
            
            # Poll for image completion
            start_time = time.time()
            completed_data = None
            
            while time.time() - start_time < self.max_wait_time:
                completed_data = self._check_image_status(image_id, headers)
                if completed_data:
                    break
                await asyncio.sleep(5)  # Wait for 5 seconds before checking again
            
            if not completed_data:
                logger.warning(f"Image generation timed out after {self.max_wait_time} seconds")
                return image_prompt, []
            
            if completed_data.get('status') == 'failed':
                logger.error(f"Image generation failed: {completed_data.get('error')}")
                return image_prompt, []
            
            # Get the image URL - only use the base URL
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

    # Keep the original method for fallback or reference
    async def _generate_image_for_tweet(self, tweet_text: str, personality_data: Dict[str, Any], shared_data: Dict[str, Any] = None) -> Tuple[str, List[str]]:
        """
        Generate an image for the tweet and upload it to Twitter.
        Returns a tuple of (image_prompt, media_urls).
        If generation fails, returns (None, []).
        """
        logger.info("Decided to generate an image for tweet")
        image_skill = ImageGenerationSkill({
            "enabled": True,
            "max_generations_per_day": 50,
            "supported_formats": ["png", "jpg"],
        })

        if await image_skill.can_generate():
            # Extract origin from character config using the passed shared_data
            character_config = self._get_character_config(shared_data)
            origin = character_config.get("backstory", {}).get("origin", "")

            # Generate image for the tweet
            image_prompt = self._build_image_prompt(tweet_text, personality_data, origin)
            image_result = await image_skill.generate_image(
                prompt=image_prompt,
                size=self.default_size,
                format=self.default_format
            )
            
            if image_result.get("success") and image_result.get("image_data", {}).get("url"):
                return image_prompt, [image_result["image_data"]["url"]]
        else:
            logger.warning("Image generation not available, proceeding with text-only tweet")
        
        return None, []
