import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# hack to exclude referral bonuses
def excludeReferrals(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    filtered_sentences = [sentence for sentence in sentences if "refer" not in sentence.lower() and "referral" not in sentence.lower()]
    filtered_text = " ".join(filtered_sentences)
    return filtered_text

def findSUB(url):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")

    remote_webdriver = 'remote_chromedriver'
    with webdriver.Remote(f'{remote_webdriver}:4444/wd/hub', options=options) as driver:
        driver.get(url)
        
        time.sleep(5)

        page_text = driver.find_element(By.TAG_NAME, "body").text
        non_referral_text = excludeReferrals(page_text)

        pattern = r"(?:earn|up to)?\s*(\d{1,3}(?:,\d{3})+)(?:\s*( points| miles| bonus| Aeroplan))"

        matches = re.findall(pattern, non_referral_text, re.IGNORECASE | re.DOTALL)
        foundBonuses = []
        for match in matches:
            bonus = match[0].replace(",", "")
            try:
                numerical = int(bonus)
                foundBonuses.append(numerical)
            except ValueError:
                print(f"Could not convert found bonus to an integer.")
                continue

        print(f"Maximum found bonus is: {max(foundBonuses)}")
        return max(foundBonuses)

