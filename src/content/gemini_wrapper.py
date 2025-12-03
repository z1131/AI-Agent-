import os
import google.generativeai as genai
from typing import Dict, Any
from .base import ContentGenerator

class GeminiGenerator(ContentGenerator):
    """
    Implementation using Google's Gemini API.
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate(self, topic: str) -> Dict[str, Any]:
        prompt = f"""
        You are a professional social media content creator for Xiaohongshu (Little Red Book).
        Please generate a post about "{topic}".
        
        Requirements:
        1. Title: Catchy, includes emojis, under 20 chars.
        2. Content: Engaging, uses emojis, split into paragraphs, includes 3-5 hashtags at the end.
        3. Image Prompt: A description to generate a cover image for this post using an AI image generator (like Midjourney).
        
        Output Format (JSON):
        {{
            "title": "...",
            "content": "...",
            "image_prompt": "..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Simple cleanup to ensure we get valid JSON-like structure if the model chats too much
            # In a production app, we would use more robust parsing or Function Calling.
            text = response.text
            
            # Quick and dirty JSON extraction for demo purposes
            # Ideally, we should use `response.text` and parse it as JSON.
            # For now, let's assume the model follows instructions well or use a simple parser.
            import json
            import re
            
            # Find JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "title": f"关于 {topic} 的分享",
                    "content": text,
                    "image_prompt": f"Illustration of {topic}"
                }
                
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            # Fallback to mock-like behavior on error to prevent crash
            return {
                "title": f"Error generating for {topic}",
                "content": f"Failed to generate content. Error: {str(e)}",
                "image_prompt": "Error icon"
            }
