from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = Driver(uc=True)  # uc=True enables undetected-chromedriver
url = "https://2captcha.com/demo/cloudflare-turnstile"
driver.uc_open_with_reconnect(url, 10)
driver.uc_gui_click_captcha()
elem = driver.find_element(By.TAG_NAME, '1')
print(elem.text)
time.sleep(60)