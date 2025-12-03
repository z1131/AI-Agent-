import os
from playwright.async_api import async_playwright, BrowserContext, Page
from typing import Optional

class BrowserManager:
    """
    Manages the browser lifecycle and persistent context.
    
    Attributes:
        user_data_dir (str): Path to the directory where browser data (cookies, local storage) is stored.
        headless (bool): Whether to run the browser in headless mode.
    """
    def __init__(self, user_data_dir: str = "user_data/browser_context", headless: bool = False):
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.headless = headless
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def launch(self):
        """
        Launches the browser with a persistent context.
        This ensures that cookies and other session data are saved automatically to user_data_dir.
        """
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir, exist_ok=True)

        self.playwright = await async_playwright().start()
        
        # launch_persistent_context is key for anti-detection and session persistence
        # It acts like a regular Chrome profile.
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            # Arguments to make it look more like a real browser
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
            ignore_default_args=["--enable-automation"]
        )
        
        # Create a default page
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        # Anti-detection: Modify navigator.webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def close(self):
        """Closes the browser and playwright instance."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
