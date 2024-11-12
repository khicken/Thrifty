import os, re, time, random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import numpy as np

debug = True

"""Activates scraper to estimate the price of the given image.

Args:
    img_name: Image name in the temp folder. Example: '1.png'

Returns:
    A tuple that gives the estimated item name (WIP) and price estimation.

Typical usage example:

    name, price = scraper('1.png')
"""
def scraper(img_name: str) -> tuple[str, float]:
    try:
        # create window
        service = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.binary_location = './chrome-win64/chrome.exe'
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(service=service, options=options)

        # boot into google.com like a regular human
        browser.maximize_window()
        browser.implicitly_wait(4)
        browser.get("https://www.google.com/")

        # make the google lens search
        browser.implicitly_wait(random.uniform(0.5, 2.0))
        browser.find_element(By.CLASS_NAME, 'nDcEnd').click() # click lens button
        browser.implicitly_wait(random.uniform(0.5, 2.0))
        browser.find_element(By.CLASS_NAME, 'DV7the').click() # click upload image button
        time.sleep(1)
        browser.execute_script("""
        var input = document.createElement('input');
        input.type = 'file';
        input.style.display = 'block';
        document.body.appendChild(input);
        input.onchange = function() {
            var file = input.files[0];
            console.log('File selected:', file.name);
        };
        input.click();
        """)
        time.sleep(2)
        file_input = browser.find_element(By.XPATH, '//input[@type="file"]')
        img_path = os.getcwd() + fr'\temp\{img_name}'
        file_input.send_keys(img_path)  # Change this to the path of your image file

        # scrape prices on listing page
        time.sleep(8)
        elements = browser.find_elements(By.CLASS_NAME, 'DdKZJb')

        # if debug:
        #     time.sleep(100) # for custom price analysis

        # convert price strings to prices
        prices = []
        for e in elements:
            mul = 1.0 # multiplier for curr conversion
            if re.findall('£', e.text): # convert Pound to US Dollar
                mul = 1.32
            chars = ''.join(re.findall(r'\d+\.\d+', e.text))
            if not chars: # empty string
                continue
            price = float(''.join(chars)) * mul
            prices.append(price)
        if debug:
            print(f'from {img_name}: {prices}')

        # old price estimates
        # print(f'datapoints: {len(prices)} \n median: {np.median(prices)} \n mean: {np.mean(prices)} \n 25th percentile: {np.percentile(prices, 25)} \n 10th percentile: {np.percentile(prices, 10)}')
        # print(f'min: {np.min(prices)} \n max: {np.max(prices)}')

        # price filtering
        new_prices = []
        q1, q3 = np.percentile(prices, 25), np.percentile(prices, 75)
        iqr = 1.5 * (q3 - q1)
        for p in prices:
            if p > 0 or p >= iqr: # if price is nonnegative and isn't outlier, it's valid
                new_prices.append(p)
        prices = new_prices
        
        # new price estimates
        print(f'datapoints: {len(prices)} -- median: {np.median(prices)} -- mean: {np.mean(prices)} -- 25th percentile: {np.percentile(prices, 25)} -- 10th percentile: {np.percentile(prices, 10)}')
        print(f'min: {np.min(prices)} -- max: {np.max(prices)}')

        os.remove(img_path) # bye bye
        return 'null', np.percentile(prices, 20) * 0.25
    except Exception as e:
        print(f"An error occurred: {e}")
        quit(1)
    finally:
        browser.quit()