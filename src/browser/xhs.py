import asyncio
import os
from playwright.async_api import Page

class XHSOperator:
    """
    Handles operations specific to Xiaohongshu (Little Red Book).
    """
    CREATOR_URL = "https://creator.xiaohongshu.com"
    LOGIN_SUCCESS_SELECTOR = "div.avatar-wrapper" # Example selector, might need adjustment
    
    def __init__(self, page: Page):
        self.page = page

    async def login(self):
        """
        Navigates to the creator center and waits for the user to log in manually.
        """
        print(f"Navigating to {self.CREATOR_URL}...")
        await self.page.goto(self.CREATOR_URL)
        
        print("Please scan the QR code to log in.")
        print("Waiting for login to complete...")
        
        # Wait for a specific element that appears only after login
        # We use a generous timeout because manual login takes time
        try:
            # Waiting for the avatar or a specific menu item that indicates we are logged in
            # We wait for the "Publish Note" button or the avatar element
            print("Waiting for login success indicator...")
            try:
                # Wait for either URL change OR a specific element
                # This is more robust than just URL waiting
                await self.page.wait_for_selector("text=发布笔记", timeout=300000)
            except:
                # Fallback: check if URL changed anyway
                if "creator" in self.page.url:
                    print("Selector not found, but URL looks correct.")
                else:
                    raise

            print("Login detected! Found '发布笔记' button or compatible state.")
            
            # Optional: Wait for a specific element to be sure
            # await self.page.wait_for_selector(".user-name", timeout=10000)
            
            print("Login successful.")
            
            # Save storage state explicitly as a backup (though persistent context handles it mostly)
            state_path = "user_data/xhs_state.json"
            await self.page.context.storage_state(path=state_path)
            print(f"Session state saved to {state_path}")
            
        except Exception as e:
            print(f"Login timed out or failed: {e}")
            raise e

    async def check_login_status(self) -> bool:
        """
        Checks if the current session is valid.
        """
        print(f"Checking login status at {self.CREATOR_URL}...")
        try:
            await self.page.goto(self.CREATOR_URL)
            # If we are redirected to login page, or don't see home, we are not logged in
            # Increase timeout to 15s to allow for slow loading
            # URL can be /creator/home or /new/home
            await self.page.wait_for_url(lambda url: "/home" in url, timeout=15000)
            print("Login check passed: URL is at creator home.")
            return True
        except Exception as e:
            print(f"Login check failed. Current URL: {self.page.url}")
            print(f"Error details: {e}")
            return False

    async def publish_note(self, title: str, content: str, image_path: str):
        """
        Publishes a note with the given title, content, and image.
        """
        print("Starting publish process...")
        
        # 1. Go to Creator Home if not already there
        if "/home" not in self.page.url:
            await self.page.goto(self.CREATOR_URL)
            await self.page.wait_for_selector("text=发布笔记")

        # 2. Click "Publish Note" button
        print("Clicking 'Publish Note'...")
        # There might be a specific button or a side menu. 
        # Usually it's a big button or a menu item "发布笔记"
        await self.page.click("text=发布笔记")
        
        # 3. Handle Image Upload
        print(f"Uploading image: {image_path}...")
        await self.page.wait_for_url("**/publish/publish**")
        
        # CRITICAL: Switch to "上传图文" (Image/Text) tab
        # The default might be Video, so we must switch.
        print("Switching to '上传图文' tab...")
        try:
            # Try to click the tab. Selector might vary, checking text is safest.
            await self.page.click("text=上传图文")
            # Wait for the image upload area to be ready (e.g. "拖拽图片" or similar text, or just a short sleep)
            await asyncio.sleep(2) 
        except Exception as e:
            print(f"Warning: Could not switch tab (maybe already there?): {e}")

        # Upload file
        # We use set_input_files directly on the input element. 
        # We don't use expect_file_chooser because we are not clicking a button to open a dialog,
        # we are directly setting the file on the hidden input.
        try:
            # Try to find the file input. 
            # XHS might have multiple, we want the one that accepts images.
            await self.page.set_input_files("input[type='file']", image_path)
        except Exception as e:
            print(f"Upload failed with generic selector, trying specific accept attribute: {e}")
            # Fallback: try to find input with accept image
            await self.page.set_input_files("input[accept*='image']", image_path)

        print("Image uploaded. Waiting for editor to load...")
        # Wait for the title input to appear. This indicates the upload was accepted and we are in edit mode.
        # The previous selector .file-list might be outdated or dynamic.
        await self.page.wait_for_selector("input[placeholder*='标题']", timeout=60000)
        
        # 4. Fill Title
        print(f"Filling title: {title}...")
        # Selector for title input. Usually has placeholder "填写标题..."
        await self.page.fill("input[placeholder*='标题']", title)
        
        # 5. Fill Content
        print("Filling content...")
        # Selector for content editor. Usually a div with contenteditable or specific class.
        # XHS often uses a div with id="post-textarea" or similar, or just look for placeholder "填写正文"
        await self.page.fill(".ql-editor, #post-textarea, div[contenteditable='true']", content)
        
        # 6. Click Publish
        print("Clicking Publish button...")
        
        # --- AGENTIC WORKFLOW DEMO ---
        # Instead of hardcoded selector, we use SmartLocator
        from src.browser.smart_locator import SmartLocator
        smart = SmartLocator(self.page)
        
        print("[Agent] Asking AI to find the 'Publish' button...")
        # We describe what we want, not how to find it
        submit_btn = await smart.find("The main submit button that says '发布' or 'Post'")
        
        if await submit_btn.count() > 0:
            await submit_btn.click()
        else:
            print("[Agent] AI failed to find button, falling back to hardcoded selector.")
            submit_btn = self.page.locator("button.submit, button:has-text('发布')").last
            await submit_btn.click()
        # -----------------------------
        
        print("Publish clicked. Waiting for success...")
        # 7. Wait for success
        # Usually redirects to success page or shows a toast
        try:
            await self.page.wait_for_selector("text=发布成功", timeout=10000)
            print("Publish Successful!")
        except:
            print("Warning: Did not see 'Publish Successful' message, but button was clicked. Check browser.")
