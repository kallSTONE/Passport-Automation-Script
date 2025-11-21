# pip install selenium beautifulsoup4 lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import os


URL = "https://www.ethiopianpassportservices.gov.et/request-appointment"


def save_and_extract(step_idx, driver):
    """Save HTML and extract native inputs, textareas, selects"""
    html = driver.page_source
    fname = f"step{step_idx}.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Saved {fname}")

    soup = BeautifulSoup(html, "lxml")

    # Native inputs and textareas
    print("\n=== INPUTS / TEXTAREAS ===")
    for el in soup.find_all(["input", "textarea"]):
        print(
            "TAG:", el.name,
            "| type:", el.get("type"),
            "| name:", el.get("name"),
            "| id:", el.get("id"),
            "| placeholder:", (el.get("placeholder") or "").strip()
        )

    # Native selects
    print("\n=== SELECTS + OPTIONS ===")
    for sel in soup.find_all("select"):
        print(f"\nSELECT name={sel.get('name')} id={sel.get('id')}")
        for opt in sel.find_all("option"):
            value = opt.get("value")
            label = (opt.text or "").strip()
            print(f"  - value={value!r} label={label!r}")


def handle_custom_dropdowns(driver):
    """Detect and print options from custom React-style dropdowns"""
    for css in ["[role='combobox']", ".react-select__control", "[aria-haspopup='listbox']"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, css)
            el.click()
            time.sleep(0.5)
            opts = driver.find_elements(By.CSS_SELECTOR, "[role='option'], .react-select__option")
            if opts:
                print("\n=== CUSTOM COMBOBOX OPTIONS ===")
                for o in opts:
                    print("  -", o.text.strip())
            # Collapse dropdown by pressing Escape
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            break
        except Exception:
            pass


def try_click_next(driver):
    """Attempt to click Next/Submit buttons"""
    wait = WebDriverWait(driver, 5)
    candidate_xpaths = [
        "//button[@type='submit' and not(@disabled)]",
        "//button[contains(translate(., 'NEXT', 'next'),'next') and not(@disabled)]",
        "//button[contains(., 'Continue') and not(@disabled)]",
        "//input[@type='submit' and not(@disabled)]",
    ]

    for xp in candidate_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return True
        except Exception:
            continue
    return False


def get_driver():
    """Configure and return Edge WebDriver"""
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


def main():
    driver = get_driver()
    driver.maximize_window()
    driver.get(URL)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    input("[!] Please complete any required checkboxes, agreements, or initial clicks, "
          "then press Enter here to continue...")

    step = 1
    while True:
        time.sleep(2)  # allow dynamic content to render
        save_and_extract(step, driver)
        handle_custom_dropdowns(driver)

        advanced = try_click_next(driver)
        if not advanced:
            print("\n[!] Could not find a Next/Submit button or no more steps.")
            break

        time.sleep(2)  # wait for next view to load
        step += 1

    driver.quit()


if __name__ == "__main__":
    main()
