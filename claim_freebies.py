import time
from playwright.sync_api import sync_playwright

USER_KEY = "LMS93"
STORE_URL = "https://store.pgatourgolfshootout.concretesoftware.com/"

def run():
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Navigating to store...")
        page.goto(STORE_URL, wait_until="networkidle")

        # 1. Handle Login
        try:
            # Look for a Login button/link at top
            login_btn = page.get_by_role("button", name="Log in")
            if login_btn.is_visible():
                login_btn.click()
                page.wait_for_timeout(1000)

            # Input User Key if prompt/input appears
            input_box = page.locator("input[type='text'], input[placeholder*='key' i]")
            if input_box.is_visible():
                input_box.fill(USER_KEY)
                
                # Submit login form
                submit_btn = page.get_by_role("button", name="Submit")
                if submit_btn.is_visible():
                    submit_btn.click()
                else:
                    input_box.press("Enter")
                
                page.wait_for_timeout(3000)
                print("Logged in successfully.")
        except Exception as e:
            print(f"Login step bypassed or error: {e}")

        # 2. Click all "Get Free" or "Get free" buttons
        # Using exact case-insensitive regex matching for "Get Free"
        free_buttons = page.get_by_role("button", name=r"/get free/i").all()
        
        if not free_buttons:
            # Fallback CSS selector search in case it's styled as a div/a rather than a native <button>
            free_buttons = page.locator("text=/Get Free/i").all()

        print(f"Found {len(free_buttons)} free item(s) to claim.")

        for idx, btn in enumerate(free_buttons, start=1):
            try:
                if btn.is_visible():
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    print(f"Successfully clicked 'Get Free' button #{idx}")
                    page.wait_for_timeout(2000)  # Wait for claim animation/network request
            except Exception as e:
                print(f"Failed to click button #{idx}: {e}")

        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()