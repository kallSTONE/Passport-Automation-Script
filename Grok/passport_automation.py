import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

# URL and constants
URL = "https://www.ethiopianpassportservices.gov.et/request-appointment"

# Load client data from JSON (example path; update as needed)
json_file_path = "client_data.json"
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"Client data file not found: {json_file_path}")
with open(json_file_path, 'r', encoding='utf-8') as f:
    client_data = json.load(f)

# Initialize Edge WebDriver with webdriver_manager
driver = webdriver.Edge(EdgeChromiumDriverManager().install())

try:
    # Step 1: Initial Agreement
    driver.get(URL)
    wait = WebDriverWait(driver, 20)  # Increased timeout for initial load
    agree_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and following-sibling::label[contains(text(), 'I agree to the terms and conditions')]]")))
    if not agree_checkbox.is_selected():
        agree_checkbox.click()
    print("Checked 'I agree to the terms and conditions'.")
    
    start_anchor = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[descendant::p//span[text()='Start Individual Appointment']]")))
    start_anchor.click()
    print("Clicked 'Start Individual Appointment'.")

    # Step 2: Appointment Type
    new_passport_anchor = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[descendant::strong[text()='New Passport'] and descendant::p[contains(text(), 'First time applicants')]]")))
    new_passport_anchor.click()
    print("Selected 'New Passport' appointment type.")
 
    # Step 3: Site Selection Form (Manual Cloudflare wait)
    print("Waiting for Cloudflare check (manual intervention needed for ~20s spinner).")
    input("Press Enter after manual step and Cloudflare check...")
    
    # Select dropdown values
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
    Select = driver.find_element(By.NAME, "siteLocationId").find_element(By.XPATH, "//option[@value='23']")
    Select.click()
    print("Selected Site Location: Central Ethiopia Regional State")
    
    Select = driver.find_element(By.NAME, "cityId").find_element(By.XPATH, "//option[@value='33']")
    Select.click()
    print("Selected City: Hossana")
    
    Select = driver.find_element(By.NAME, "officeId").find_element(By.XPATH, "//option[@value='39']")
    Select.click()
    print("Selected Office: Hossana ICS")
    
    Select = driver.find_element(By.NAME, "deliverySiteId").find_element(By.XPATH, "//option[@value='19']")
    Select.click()
    print("Selected Delivery Site: Hossana ICS Office")

    # Step 4: Date & Time Form Input
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

    # Step  5: Applicant Details Form
    wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
    driver.find_element(By.NAME, "firstName").clear()
    driver.find_element(By.NAME, "firstName").send_keys(client_data["firstName"])
    print(f"Filled first name: {client_data['firstName']}")
    
    driver.find_element(By.NAME, "middleName").clear()
    driver.find_element(By.NAME, "middleName").send_keys(client_data["middleName"])
    print(f"Filled middle name: {client_data['middleName']}")
    
    driver.find_element(By.NAME, "lastName").clear()
    driver.find_element(By.NAME, "lastName").send_keys(client_data["lastName"])
    print(f"Filled last name: {client_data['lastName']}")
    
    driver.find_element(By.NAME, "geezFirstName").clear()
    driver.find_element(By.NAME, "geezFirstName").send_keys(client_data["geezFirstName"])
    print(f"Filled geez first name: {client_data['geezFirstName']}")
    
    driver.find_element(By.NAME, "geezMiddleName").clear()
    driver.find_element(By.NAME, "geezMiddleName").send_keys(client_data["geezMiddleName"])
    print(f"Filled geez middle name: {client_data['geezMiddleName']}")
    
    driver.find_element(By.NAME, "geezLastName").clear()
    driver.find_element(By.NAME, "geezLastName").send_keys(client_data["geezLastName"])
    print(f"Filled geez last name: {client_data['geezLastName']}")
    
    driver.find_element(By.ID, "date-picker-dialog").clear()
    driver.find_element(By.ID, "date-picker-dialog").send_keys(client_data["DOB"])
    print(f"Filled DOB: {client_data['DOB']}")
    
    driver.find_element(By.NAME, "birthPlace").clear()
    driver.find_element(By.NAME, "birthPlace").send_keys(client_data["birthPlace"])
    print(f"Filled birth place: {client_data['birthPlace']}")
    
    driver.find_element(By.NAME, "phoneNumber").clear()
    driver.find_element(By.NAME, "phoneNumber").send_keys(client_data["phoneNumber"])
    print(f"Filled phone number: {client_data['phoneNumber']}")
    
    driver.find_element(By.NAME, "nationalityId").find_element(By.XPATH, "//option[@value='1']").click()
    print("Selected nationality: ETHIOPIA")
    
    driver.find_element(By.NAME, "gender").find_element(By.XPATH, "//option[@value='1']").click()  # Male
    print("Selected gender: Male")
    
    driver.find_element(By.NAME, "martialStatus").find_element(By.XPATH, "//option[@value='0']").click()  # Single
    print("Selected marital status: Single")
    
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
    next_button.click()
    print("Clicked 'Next' on Applicant Details form.")

    # Step 6: Address Form
    wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='region']")))
    driver.find_element(By.XPATH, "//select[preceding-sibling::label[text()='region']]").find_element(By.XPATH, "//option[contains(text(), 'Central Ethiopia Regional State')]").click()
    print("Selected region: Central Ethiopia Regional State")
    
    driver.find_element(By.NAME, "city").clear()
    driver.find_element(By.NAME, "city").send_keys("Hossana")
    print("Filled city: Hossana")
    
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
    next_button.click()
    print("Clicked 'Next' on Address form.")

    # Step 7: Family Details Form
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[descendant::span[text()='Next']]")))
    next_button.click()
    print("Clicked 'Next' on Family Details form.")

    # Step 8: Passport Pages Form (Manual Cloudflare wait)
    print("Waiting for Cloudflare check (manual intervention needed for ~20s spinner).")
    input("Press Enter after manual step and Cloudflare check...")

    # Step 9: Upload Documents
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

    # Step 10: Confirm Applicant Details (Manual intervention)
    print("Waiting for manual confirmation of applicant details.")
    input("Press Enter after manual step...")

    # Step 11: Payment Selection
    payment_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'types') and contains(text(), 'Pay with CBE Mobile')]")))
    payment_option.click()
    print("Clicked 'Pay with CBE Mobile' payment option.")
    
    terms_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and following-sibling::label[contains(text(), 'Agree to terms and conditions')]]")))
    if not terms_checkbox.is_selected():
        terms_checkbox.click()
    print("Checked 'Agree to terms and conditions'.")
    
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and descendant::span[text()='Next']]")))
    submit_button.click()
    print("Clicked 'Next' on Payment Selection.")

    # Step 12: Instruction Page (Manual extraction)
    print("Reached Instruction Page. Manually extract Order Code and Application Number.")
    input("Press Enter after manual extraction...")

except TimeoutException as e:
    print(f"Timeout error: {e}. Please fix the issue manually and press Enter to continue.")
    input("Press Enter to resume...")
except NoSuchElementException as e:
    print(f"Element not found: {e}. Please fix the issue manually and press Enter to continue.")
    input("Press Enter to resume...")
except FileNotFoundError as e:
    print(f"File error: {e}. Please fix the issue manually and press Enter to continue.")
    input("Press Enter to resume...")
except Exception as e:
    print(f"Unexpected error: {e}. Please fix the issue manually and press Enter to continue.")
    input("Press Enter to resume...")

# Keep browser open for manual intervention
print("Script paused. Browser remains open. Fix issues and press Enter in the console to resume or close the browser manually.")
input("Press Enter to close the browser or resume...")

driver.quit()
