# demo_cloudflare_turnstile.py
# pip install selenium requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

URL = "https://2captcha.com/demo/cloudflare-turnstile"

# Replace with your 2Captcha API key (sign up at https://2captcha.com/ and get the key)
API_KEY = "YOUR_2CAPTCHA_API_KEY_HERE"  # e.g., "1234567890abcdef1234567890abcdef"

def get_driver():
    """Configure and return Edge WebDriver."""
    from selenium.webdriver.edge.options import Options
    opts = Options()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Edge(options=opts)
    print("[+] Using Edge WebDriver")
    return driver

def solve_turnstile(driver, api_key):
    """Solve Cloudflare Turnstile using 2Captcha API."""
    # Find the sitekey from the Turnstile widget
    try:
        turnstile_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cf-turnstile"))
        )
        sitekey = turnstile_div.get_attribute("data-sitekey")
        print(f"[+] Found sitekey: {sitekey}")
    except Exception as e:
        print(f"[!] Failed to find sitekey: {e}")
        return None

    # Step 1: Send CAPTCHA to 2Captcha
    captcha_url = "https://2captcha.com/in.php"
    params = {
        "key": api_key,
        "method": "turnstile",
        "sitekey": sitekey,
        "pageurl": URL,
        "json": 1
    }
    response = requests.post(captcha_url, params=params)
    if response.status_code != 200:
        print(f"[!] Error sending to 2Captcha: {response.text}")
        return None

    result = response.json()
    if result["status"] != 1:
        print(f"[!] 2Captcha error: {result['request']}")
        return None

    captcha_id = result["request"]
    print(f"[+] CAPTCHA sent to 2Captcha, ID: {captcha_id}")

    # Step 2: Poll for the solution (wait 15-30s typically)
    token = None
    for _ in range(30):  # Max 5 minutes (10s intervals)
        time.sleep(10)
        result_url = "https://2captcha.com/res.php"
        params = {
            "key": api_key,
            "action": "get",
            "id": captcha_id,
            "json": 1
        }
        response = requests.get(result_url, params=params)
        result = response.json()

        if result["status"] == 1:
            token = result["request"]
            print(f"[+] Got token: {token}")
            break
        elif "CAPCHA_NOT_READY" not in result["request"]:
            print(f"[!] 2Captcha error: {result['request']}")
            return None

    if not token:
        print("[!] Timed out waiting for token")
        return None

    # Step 3: Inject the token into the page
    try:
        driver.execute_script(f"document.querySelector('[name=\"cf-turnstile-response\"]').value = '{token}';")
        print("[+] Injected token into response field")
    except Exception as e:
        print(f"[!] Failed to inject token: {e}")
        return None

    return token

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
    if API_KEY == "YOUR_2CAPTCHA_API_KEY_HERE":
        print("[!] Please replace API_KEY with your actual 2Captcha API key.")
        return

    driver = get_driver()
    try:
        driver.maximize_window()
        driver.get(URL)
        print(f"[+] Navigated to {URL}")

        # Wait for page body
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        print("[+] Page body detected")

        # Solve Turnstile
        token = solve_turnstile(driver, API_KEY)
        if not token:
            print("[!] Failed to solve Turnstile")
            return

        # Submit the form (adjust selector if needed for the demo page)
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()
            print("[+] Submitted the form")
        except Exception as e:
            print(f"[!] Failed to submit form: {e}")

        # Wait to see the result (e.g., success message)
        time.sleep(5)  # Give time for page to update

        # Save snapshot
        save_snapshot(driver, name_prefix="turnstile_demo")

        # Pause for manual inspection
        input("[!] Check the browser to see if it passed. Press ENTER to quit...")

    finally:
        driver.quit()
        print("[+] Browser closed.")

if __name__ == "__main__":
    main()