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
            # Check if user input box is visible or open modal
            input_box = page.locator("input#user-id-input, input[placeholder*='M3WMG' i], input[placeholder*='key' i]").first
            if not input_box.is_visible():
                login_trigger = page.locator("button:has-text('Log in')").first
                if login_trigger.is_visible():
                    login_trigger.click()
                    page.wait_for_timeout(1000)

            input_box = page.locator("input#user-id-input, input[placeholder*='M3WMG' i], input[placeholder*='key' i]").first
            if input_box.is_visible():
                input_box.fill(USER_KEY)
                
                # Submit login modal via modal continue button
                submit_btn = page.locator("[data-type='user-id-button-continue'], .user-id-modal__button").first
                if submit_btn.is_visible():
                    submit_btn.click()
                    page.wait_for_timeout(3000)
                else:
                    input_box.press("Enter")
                    page.wait_for_timeout(3000)
            
            # Verify modal closed
            if not page.locator(".user-id-modal__container").is_visible():
                print("Logged in successfully.")
            else:
                print("Warning: Login modal still present.")
        except Exception as e:
            print(f"Login step exception: {e}")

        # 2. Check items to claim vs owned items
        owned_buttons = page.locator("button:has-text('Owned'), [data-testid='owned']").all()
        if owned_buttons:
            print(f"Found {len(owned_buttons)} item(s) already claimed ('Owned').")

        # Select free item buttons
        free_buttons = page.locator("[data-id='get-free'], [data-testid='get-free'], button:has-text('Get free'), button:has-text('Free')").all()
        
        claimable_buttons = []
        for btn in free_buttons:
            try:
                txt = btn.inner_text().strip().lower()
                if btn.is_visible() and "owned" not in txt:
                    claimable_buttons.append(btn)
            except Exception:
                pass

        print(f"Found {len(claimable_buttons)} free item(s) to claim.")

        for idx, btn in enumerate(claimable_buttons, start=1):
            try:
                if btn.is_visible():
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    print(f"Successfully clicked 'Get Free' button #{idx}")
                    page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Failed to click button #{idx}: {e}")

        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()