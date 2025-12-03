import os
from openai import OpenAI
from typing import Dict, Any
from .base import ContentGenerator
import json
import re

class DeepSeekGenerator(ContentGenerator):
    """
    Implementation using DeepSeek API (OpenAI-compatible).
    """
    
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
        
        # DeepSeek uses OpenAI client but with a different base URL
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"

    def generate(self, topic: str) -> Dict[str, Any]:
        system_prompt = """
        You are a professional social media content creator for Xiaohongshu (Little Red Book).
        Output strictly in JSON format.
        """
        
        user_prompt = f"""
        Please generate a post about "{topic}".
        
        Requirements:
        1. Title: Catchy, includes emojis, under 20 chars.
        2. Content: Engaging, uses emojis, split into paragraphs, includes 3-5 hashtags at the end.
        3. Image Prompt: A description to generate a cover image for this post using an AI image generator.
        
        Output Format (JSON):
        {{
            "title": "...",
            "content": "...",
            "image_prompt": "..."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" } # DeepSeek supports JSON mode
            )
            
            content_str = response.choices[0].message.content
            
            # Parse JSON
            try:
                return json.loads(content_str)
            except json.JSONDecodeError:
                # Fallback if strict JSON mode fails or returns markdown wrapped json
                match = re.search(r'\{.*\}', content_str, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    raise ValueError("Could not parse JSON from response")
                
        except Exception as e:
            print(f"Error calling DeepSeek: {e}")
            return {
                "title": f"Error generating for {topic}",
                "content": f"Failed to generate content. Error: {str(e)}",
                "image_prompt": "Error icon"
            }
