import os, re, time, random
import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from amazoncaptcha import AmazonCaptcha

img_url = os.getcwd() + r'\samples\waterbottle2.png'

# create window
service = Service('./chromedriver.exe')
options = webdriver.ChromeOptions()
options.binary_location = './chrome-win64/chrome.exe'
options.add_argument('--headless') # comment when testing
browser = webdriver.Chrome(service=service, options=options)

# boot into google.com like a regular human
browser.maximize_window()
browser.implicitly_wait(5)
browser.get("https://www.google.com/")

# make the google lens search
browser.implicitly_wait(random.uniform(0.5, 2.0))
browser.find_element(By.CLASS_NAME, 'nDcEnd').click() # click lens button
browser.implicitly_wait(random.uniform(0.5, 2.0))
browser.find_element(By.CLASS_NAME, 'DV7the').click() # click upload image button
time.sleep(1)
pyautogui.write(img_url) # upload image
pyautogui.press('enter')
browser.implicitly_wait(3)
try:
    # Wait up to 10 seconds for elements with class 'DdKZJb' to be present
    elements = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'oOZ3vf'))
    )

    # Iterate through each element and print its text
    for e in elements:
        print(f'found: {e.text}')

except Exception as e:
    print(f"An error occurred: {e}")
    
time.sleep(10000)

browser.get("https://www.amazon.com/Stanley-IceFlow-Stainless-Steel-Tumbler/dp/B0CT4BB651")
browser.find_element_by_class_name

# terminate program
browser.quit()

'''  Returns a float (price) given a url  '''
def scraper(url: str) -> float:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.84 Safari/537.3'
    }
    

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