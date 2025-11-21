# demo_turnstile_edge.py
# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

URL = "https://2captcha.com/demo/cloudflare-turnstile"

def get_driver():
    """Configure and return Edge WebDriver (same options as your longer script)."""
    from selenium.webdriver.edge.options import Options
    opts = Options()
    # Stability tweaks
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    # Reduce Selenium detectability
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Edge(options=opts)
    print("[+] Using Edge WebDriver")
    return driver

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
    driver = get_driver()
    try:
        driver.maximize_window()
        driver.get(URL)
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

        # Save HTML + screenshot (diagnostic)
        save_snapshot(driver, name_prefix="turnstile_demo")

        # Pause for manual interaction; this does not bypass anything.
        input("[!] Manual step: interact with the opened browser as needed. Press ENTER here to quit and close the browser...")

    finally:
        driver.quit()
        print("[+] Browser closed.")

if __name__ == "__main__":
    main()
