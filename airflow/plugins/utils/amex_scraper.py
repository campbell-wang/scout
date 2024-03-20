import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def amexScraper(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    remote_webdriver = 'remote_chromedriver'
    with webdriver.Remote(f'{remote_webdriver}:4444/wd/hub', options=options) as driver:
        driver.get(url)

        time.sleep(5)

        signup_bonus = 0

        try:
            signup_bonus_element = driver.find_element(By.CSS_SELECTOR, '.sc_at_box_root.sc_bgColor_deep-blue.sc_rounded_sm')
            signup_bonus_text = signup_bonus_element.text
        except:
            try:
                signup_bonus_element = driver.find_element(By.CSS_SELECTOR, ".sc_se_pentagon-and-zero-apr-composable-banner_nonStripeContentWrapper.sc_bgColor_transparent.sc_padding_0.sc_rounded_sm")
                signup_bonus_text = signup_bonus_element.text
            except:
                signup_bonus_text = ""

        if signup_bonus_text:
            numbers = [int(s.replace(',', '')) for s in signup_bonus_text.split() if s.replace(',', '').isdigit()]
            if numbers:
                signup_bonus = max(numbers)
        
        return signup_bonus
