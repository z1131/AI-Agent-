import asyncio
import argparse
import sys
import os

# Add src to python path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.context import BrowserManager
from src.browser.xhs import XHSOperator

from src.content.mock import MockGenerator
from src.content.gemini_wrapper import GeminiGenerator
from src.content.deepseek_wrapper import DeepSeekGenerator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def login_task():
    """
    Task to perform manual login and save session.
    """
    # For login, we want to see the browser (headless=False)
    browser_manager = BrowserManager(headless=False)
    try:
        await browser_manager.launch()
        xhs = XHSOperator(browser_manager.page)
        await xhs.login()
        
        # Keep browser open for a few seconds to let user see success
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error during login: {e}")
    finally:
        await browser_manager.close()

def generate_task(topic: str, provider: str) -> dict:
    """
    Task to generate content. Returns the result dict.
    """
    print(f"Generating content for topic: '{topic}' using {provider}...")
    
    if provider == "gemini":
        generator = GeminiGenerator()
    elif provider == "deepseek":
        generator = DeepSeekGenerator()
    else:
        generator = MockGenerator()
        
    result = generator.generate(topic)
    
    print("\n" + "="*30)
    print(f"TITLE: {result.get('title')}")
    print("-" * 30)
    print(f"CONTENT:\n{result.get('content')}")
    print("-" * 30)
    print(f"IMAGE PROMPT: {result.get('image_prompt')}")
    print("="*30 + "\n")
    
    return result

async def publish_task(topic: str, provider: str):
    """
    Task to generate AND publish content.
    """
    # 1. Generate Content
    content_data = generate_task(topic, provider)
    
    # 2. Prepare Image (Using local test image for now)
    image_path = os.path.abspath("test_image.jpg")
    if not os.path.exists(image_path):
        print(f"Error: Test image not found at {image_path}. Please run 'curl -o test_image.jpg https://picsum.photos/800/600' first.")
        return

    # 3. Publish via Browser
    print("Launching browser for publishing...")
    # headless=False so we can see what's happening
    browser_manager = BrowserManager(headless=False)
    try:
        await browser_manager.launch()
        xhs = XHSOperator(browser_manager.page)
        
        # Ensure logged in
        if not await xhs.check_login_status():
            print("Not logged in! Please run 'login' command first.")
            return

        await xhs.publish_note(
            title=content_data.get("title"),
            content=content_data.get("content"),
            image_path=image_path
        )
        
        # Keep open briefly to see result
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"Error during publishing: {e}")
    finally:
        await browser_manager.close()

def main():
    parser = argparse.ArgumentParser(description="AI Self-Media Operation Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Open browser to login manually")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate content")
    gen_parser.add_argument("--topic", required=True, help="Topic to generate content for")
    gen_parser.add_argument("--provider", default="mock", choices=["mock", "gemini", "deepseek"], help="AI Provider")

    # Publish command
    pub_parser = subparsers.add_parser("publish", help="Generate and Publish content")
    pub_parser.add_argument("--topic", required=True, help="Topic to publish")
    pub_parser.add_argument("--provider", default="mock", choices=["mock", "gemini", "deepseek"], help="AI Provider")

    args = parser.parse_args()

    if args.command == "login":
        asyncio.run(login_task())
    elif args.command == "generate":
        generate_task(args.topic, args.provider)
    elif args.command == "publish":
        asyncio.run(publish_task(args.topic, args.provider))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
