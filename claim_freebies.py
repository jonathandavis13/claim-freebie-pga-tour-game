import time
from playwright.sync_api import sync_playwright

USER_KEY = "LMS93"
STORE_URL = "https://store.pgatourgolfshootout.concretesoftware.com/"

def run():
    with sync_playwright() as p:
        # Launch headed browser for debugging (slow_mo helps observe actions)
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(viewport={"width":1280, "height":800})
        page = context.new_page()

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Navigating to store...")
        page.goto(STORE_URL, wait_until="networkidle")

        # Pause here to allow interactive debugging in headed mode
        try:
            page.pause()
        except Exception:
            # page.pause may not work in some environments; ignore if it fails
            pass

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

        # 2. Click all "Get Free" or "Get free" controls
        # Try role-based lookup first (native buttons), then text, then attribute selectors
        free_buttons = page.get_by_role("button", name=r"/get free/i").all()

        if not free_buttons:
            free_buttons = page.locator("text=/Get Free/i").all()

        if not free_buttons:
            # Fallback to attribute-based selectors (e.g. <span data-id="get-free" ...>)
            free_buttons = page.locator('[data-id="get-free"], [data-testid="get-free"], span[data-id], span[data-testid]').all()

        print(f"Found {len(free_buttons)} free item(s) to claim.")

        for idx, btn in enumerate(free_buttons, start=1):
            try:
                # Wait until attached and visible
                try:
                    btn.wait_for(state="visible", timeout=5000)
                except Exception:
                    pass

                if not btn.is_visible():
                    print(f"Button #{idx} not visible, skipping.")
                    continue

                btn.scroll_into_view_if_needed()

                # Try normal click, then force click, then JS click as fallbacks
                clicked = False
                try:
                    btn.click(timeout=5000)
                    clicked = True
                except Exception:
                    try:
                        btn.click(force=True, timeout=5000)
                        clicked = True
                    except Exception:
                        try:
                            btn.evaluate("el => el.click()")
                            clicked = True
                        except Exception as e:
                            print(f"JS-click fallback failed for button #{idx}: {e}")

                if clicked:
                    print(f"Successfully clicked 'Get Free' control #{idx}")
                    page.wait_for_timeout(2000)  # Wait for claim animation/network request
                else:
                    print(f"Failed to click button #{idx} by any method.")
            except Exception as e:
                print(f"Failed to handle button #{idx}: {e}")

        browser.close()
        print("Done!")

if __name__ == "__main__":
    run()