import os
from openai import OpenAI
from playwright.async_api import Page, Locator
from bs4 import BeautifulSoup
import re

class SmartLocator:
    """
    Uses LLM (DeepSeek) to find elements on the page using natural language descriptions.
    """
    def __init__(self, page: Page):
        self.page = page
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"

    async def find(self, description: str) -> Locator:
        """
        Finds an element based on description.
        """
        # 1. Get simplified HTML
        # We only want the body, and we want to strip scripts/styles to save tokens
        html_content = await self.page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove clutter
        for tag in soup(['script', 'style', 'svg', 'path', 'meta', 'link', 'noscript']):
            tag.decompose()
            
        # Further simplify: remove comments and empty lines
        clean_html = "\n".join([line.strip() for line in soup.body.prettify().split("\n") if line.strip()])
        
        # Truncate if too long (simple safety mechanism)
        # DeepSeek has 32k context, but let's be safe and efficient.
        # If the page is huge, this approach needs refinement (e.g. accessibility tree).
        if len(clean_html) > 20000:
            clean_html = clean_html[:20000] + "...(truncated)"

        # 2. Ask LLM
        prompt = f"""
        I have an HTML page. I need to find the CSS selector for an element described as: "{description}".
        
        Here is the cleaned HTML of the page:
        ```html
        {clean_html}
        ```
        
        Return ONLY the CSS selector. Do not include any explanation or markdown formatting. 
        If there are multiple matches, choose the most specific and robust one.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful QA automation engineer. Return only the CSS selector."},
                    {"role": "user", "content": prompt}
                ]
            )
            selector = response.choices[0].message.content.strip()
            # Clean up if LLM returns code blocks
            selector = selector.replace("```css", "").replace("```", "").strip()
            
            print(f"[SmartLocator] Description: '{description}' -> Selector: '{selector}'")
            return self.page.locator(selector).first
            
        except Exception as e:
            print(f"[SmartLocator] Error finding element: {e}")
            raise e
