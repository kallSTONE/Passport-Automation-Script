# demo_turnstile_edge_seleniumbase.py
# pip install seleniumbase

from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

URL = "https://2captcha.com/demo/cloudflare-turnstile"

def save_snapshot(driver, name_prefix="demo"):
    """Save page HTML and a screenshot for debugging/records."""
    html = driver.page_source
    html_fname = f"{name_prefix}.html"
    with open(html_fname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Saved HTML -> {html_fname}")

    screenshot_fname = f"{name_prefix}.png"
    driver.save_screenshot(screenshot_fname)
    print(f"[+] Saved screenshot -> {screenshot_fname}")

def main():
    # Configure Edge arguments (mimicking original script)
    extra_args = [
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-automation",  # Replaces excludeSwitches["enable-automation"]
        "--disable-blink-features=AutomationControlled"  # Replaces useAutomationExtension=False
    ]

    # Initialize SeleniumBase Driver with Edge and custom arguments
    driver = Driver(browser="edge", headless=False, extra_args=extra_args)
    print("[+] Using Edge via SeleniumBase")

    try:
        driver.maximize_window()
        driver.get(URL)  # Standard get (no uc_open_with_reconnect, as uc is Chrome-only)
        print(f"[+] Navigated to {URL}")

        # Wait for page body to be present (up to 20s)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        print("[+] Page body detected")

        # Optional: wait briefly for Turnstile iframe/widget if present
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='turnstile']")))
            print("[+] Turnstile iframe detected")
        except Exception:
            print("[!] Turnstile iframe not detected within 10s — continuing anyway")

        # Attempt to click Turnstile captcha (fall back to standard Selenium click)
        try:
            # Refined selector for Turnstile checkbox
            captcha = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][class*='cf-turnstile']")
            driver.execute_script("arguments[0].click();", captcha)  # JavaScript click to avoid detection
            print("[+] Attempted to click Turnstile captcha")
        except Exception as e:
            print(f"[!] Failed to click captcha: {e}")
            save_snapshot(driver, name_prefix="captcha_failure")

        # Attempt to find element (using h1 as placeholder, adjust if needed)
        try:
            elem = driver.find_element(By.TAG_NAME, "h1")  # Example: find first <h1> tag
            print(f"[+] Found element text: {elem.text}")
        except Exception as e:
            print(f"[!] Failed to find element: {e}")

        # Save HTML + screenshot (diagnostic)
        save_snapshot(driver, name_prefix="turnstile_demo_edge")

        # Pause to observe results
        input("[!] Manual step: check the browser for captcha result. Press ENTER to quit...")

    finally:
        driver.quit()
        print("[+] Browser closed.")

if __name__ == "__main__":
    main()