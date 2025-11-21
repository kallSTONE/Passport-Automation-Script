# pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
import json
import os
import time

# URL and constants
URL = "https://www.ethiopianpassportservices.gov.et/request-appointment"
json_file_path = "client_data.json"

# Load client data from JSON with UTF-8 encoding
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Client data file not found: {json_file_path}")
with open(json_file_path, 'r', encoding='utf-8') as f:
    client_data = json.load(f)

def get_driver():
    """Configure and return Edge WebDriver"""
    opts = Options()
    # Stability tweaks
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    # Reduce Selenium detectability
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Assuming msedgedriver.exe is in the script directory or PATH
    try:
        driver = webdriver.Edge(options=opts)
        print("[+] Using Edge WebDriver")
        return driver
    except Exception as e:
        print(f"[-] WebDriver error: {e}. Ensure msedgedriver.exe is in the script directory or PATH.")
        input("Press Enter after fixing the WebDriver issue...")
        raise

def try_click_next(driver, wait):
    """Attempt to click Next/Submit buttons with specific XPaths"""
    candidate_xpaths = [
        "//button[@type='submit' and not(@disabled)]",
        "//button[descendant::span[text()='Next'] and not(@disabled)]",
        "//button[@type='button' and descendant::span[text()='Next'] and not(@disabled)]",
        "//button[@type='submit' and text()='submit' and not(@disabled)]",
    ]
    for xp in candidate_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return True
        except Exception:
            continue
    return False

def main():
    driver = get_driver()
    driver.maximize_window()
    driver.get(URL)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    step = 1
    while step <= 11:  # Limit to 11 steps (excluding manual extraction in 12)
        print(f"\n=== Step {step} ===")
        time.sleep(2)  # Allow dynamic content to render

        if step == 1:  # Initial Agreement
            agree_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type=\"checkbox\" and following-sibling::label[contains(text(), \"I agree to the terms and conditions\")]]")))
            if not agree_checkbox.is_selected():
                agree_checkbox.click()
            print("Checked 'I agree to the terms and conditions'.")
            
            start_anchor = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[descendant::p//span[text()='Start Individual Appointment']]")))
            start_anchor.click()
            print("Clicked 'Start Individual Appointment'.")

        elif step == 2:  # Appointment Type
            new_passport_anchor = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[descendant::strong[text()='New Passport'] and descendant::p[contains(text(), 'First time applicants')]]")))
            new_passport_anchor.click()
            print("Selected 'New Passport' appointment type.")

        elif step == 3:  # Site Selection Form (Manual Cloudflare wait)
            print("Waiting for Cloudflare check (manual intervention needed for ~20s spinner).")
            input("Press Enter after manual step and Cloudflare check...")
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
            driver.find_element(By.NAME, "siteLocationId").find_element(By.XPATH, "//option[@value='23']").click()
            driver.find_element(By.NAME, "cityId").find_element(By.XPATH, "//option[@value='33']").click()
            driver.find_element(By.NAME, "officeId").find_element(By.XPATH, "//option[@value='39']").click()
            driver.find_element(By.NAME, "deliverySiteId").find_element(By.XPATH, "//option[@value='19']").click()
            print("Filled Site Selection form.")

        elif step == 4:  # Date & Time Form Input
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button:not([disabled])")))
            enabled_buttons = driver.find_elements(By.CSS_SELECTOR, "button:not([disabled])")
            if enabled_buttons:
                enabled_buttons[0].click()
                print("Selected first enabled date.")
            
            desired_time = "09:00:00 - 10:00:00"
            time_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@type='button' and @value='{desired_time}']")))
            time_button.click()
            print(f"Selected time slot: {desired_time}")
            
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test="col"].next-button button.btn-primary')))
            next_button.click()
            print("Clicked 'Next' on Date & Time form.")

        elif step == 5:  # Applicant Details Form
            wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
            driver.find_element(By.NAME, "firstName").clear()
            driver.find_element(By.NAME, "firstName").send_keys(client_data["firstName"])
            driver.find_element(By.NAME, "middleName").clear()
            driver.find_element(By.NAME, "middleName").send_keys(client_data["middleName"])
            driver.find_element(By.NAME, "lastName").clear()
            driver.find_element(By.NAME, "lastName").send_keys(client_data["lastName"])
            driver.find_element(By.NAME, "geezFirstName").clear()
            driver.find_element(By.NAME, "geezFirstName").send_keys(client_data["geezFirstName"])
            driver.find_element(By.NAME, "geezMiddleName").clear()
            driver.find_element(By.NAME, "geezMiddleName").send_keys(client_data["geezMiddleName"])
            driver.find_element(By.NAME, "geezLastName").clear()
            driver.find_element(By.NAME, "geezLastName").send_keys(client_data["geezLastName"])
            driver.find_element(By.ID, "date-picker-dialog").clear()
            driver.find_element(By.ID, "date-picker-dialog").send_keys(client_data["DOB"])
            driver.find_element(By.NAME, "birthPlace").clear()
            driver.find_element(By.NAME, "birthPlace").send_keys(client_data["birthPlace"])
            driver.find_element(By.NAME, "phoneNumber").clear()
            driver.find_element(By.NAME, "phoneNumber").send_keys(client_data["phoneNumber"])
            driver.find_element(By.NAME, "nationalityId").find_element(By.XPATH, "//option[@value='1']").click()
            driver.find_element(By.NAME, "gender").find_element(By.XPATH, "//option[@value='1']").click()
            driver.find_element(By.NAME, "martialStatus").find_element(By.XPATH, "//option[@value='0']").click()
            print("Filled Applicant Details form.")
            
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
            next_button.click()
            print("Clicked 'Next' on Applicant Details form.")

        elif step == 6:  # Address Form
            wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='region']")))
            driver.find_element(By.XPATH, "//select[preceding-sibling::label[text()='region']]").find_element(By.XPATH, "//option[contains(text(), 'Central Ethiopia Regional State')]").click()
            driver.find_element(By.NAME, "city").clear()
            driver.find_element(By.NAME, "city").send_keys("Hossana")
            print("Filled Address form.")
            
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
            next_button.click()
            print("Clicked 'Next' on Address form.")

        elif step == 7:  # Family Details Form
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
            next_button.click()
            print("Clicked 'Next' on Family Details form.")

        elif step == 8:  # Passport Pages Form (Manual Cloudflare wait)
            print("Waiting for Cloudflare check (manual intervention needed for ~20s spinner).")
            input("Press Enter after manual step and Cloudflare check...")

        elif step == 9:  # Upload Documents
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='file']")))
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            gov_id_path = client_data.get("governmentIdPath")
            if not gov_id_path or not os.path.exists(gov_id_path):
                raise FileNotFoundError(f"Government ID file not found: {gov_id_path}")
            file_inputs[0].send_keys(gov_id_path)
            print(f"Uploaded government ID: {gov_id_path}")
            
            birth_cert_path = client_data.get("birthCertificatePath")
            if not birth_cert_path or not os.path.exists(birth_cert_path):
                raise FileNotFoundError(f"Birth certificate file not found: {birth_cert_path}")
            file_inputs[1].send_keys(birth_cert_path)
            print(f"Uploaded birth certificate: {birth_cert_path}")
            
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and text()='submit']")))
            submit_button.click()
            print("Clicked 'Submit' on Upload Documents.")

        elif step == 10:  # Confirm Applicant Details (Manual intervention)
            print("Waiting for manual confirmation of applicant details.")
            input("Press Enter after manual step...")

        elif step == 11:  # Payment Selection
            payment_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'types') and contains(text(), 'Pay with CBE Mobile')]")))
            payment_option.click()
            print("Clicked 'Pay with CBE Mobile' payment option.")
            
            terms_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and following-sibling::label[contains(text(), 'Agree to terms and conditions')]")))
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
            print("Checked 'Agree to terms and conditions'.")
            
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and descendant::span[text()='Next']]")))
            submit_button.click()
            print("Clicked 'Next' on Payment Selection.")

        advanced = try_click_next(driver, wait) if step < 11 else False
        if not advanced and step < 11:
            print("\n[!] Could not find a Next/Submit button. Please fix manually and press Enter to continue.")
            input("Press Enter to resume...")
        elif step == 11:
            print("\n=== Step 12: Instruction Page ===")
            print("Reached Instruction Page. Manually extract Order Code and Application Number.")
            input("Press Enter after manual extraction...")

        step += 1

    driver.quit()

if __name__ == "__main__":
    main()