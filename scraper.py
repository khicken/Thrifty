import requests
from bs4 import BeautifulSoup
import re, typing

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By

# create window
service = Service('./chromedriver.exe')
options = webdriver.ChromeOptions()
options.binary_location = './chrome-win64/chrome.exe'
driver = webdriver.Chrome(service=service, options=options)

# boot into google.com like a regular human
driver.maximize_window()
driver.get("https://www.google.com/")
driver.implicitly_wait(0.5)
driver.get("https://www.selenium.dev/selenium/web/web-form.html")

driver.quit()

print(driver.title)



print(driver.page_source)
soup = BeautifulSoup(driver.page_source, 'html.parser')

'''  Returns a float (price) given a url  '''
def scraper(url: str) -> float:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.84 Safari/537.3'
    }
    

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)

    class_names = ['a-price-whole', '']
    preprice = soup.find('span', {'class': class_names}).text

    try:
        print(f'price obtained: {float(price)}')
    except:
        price = re.sub(r'[0-9.]', '', preprice)
        if re.findall('£'): # Convert Pound to US Dollar
            price *= 1.32
    return price

# testing
print(scraper('https://www.ebay.com/itm/144732458614'))