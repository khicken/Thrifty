import os, re, time, random
import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import numpy as np

def scraper() -> list:
    try:
        # create window
        service = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.binary_location = './chrome-win64/chrome.exe'
        # options.add_argument('--headless') # need to fix this later, will have to remove pyautogui
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
        pyautogui.write(os.getcwd() + r'\temp.png') # upload image
        pyautogui.press('enter')

        # scrape prices on listing page
        time.sleep(5)
        elements = browser.find_elements(By.CLASS_NAME, 'DdKZJb')

        # time.sleep(60) # for custom price analysis

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
            print(price)
            prices.append(price)

        # old price estimates
        print(f'median: {np.median(prices)} \n mean: {np.mean(prices)} \n 25th percentile: {np.percentile(prices, 25)} \n 10th percentile: {np.percentile(prices, 10)}')
        print(f'min: {np.min(prices)} \n max: {np.max(prices)}')

        # price filtering
        q1, q3 = np.percentile(prices, 25), np.percentile(prices, 75)
        iqr = 1.5 * (q3 - q1)
        i = 0
        while i < len(prices):
            if prices[i] <= 0 or prices[i] >= iqr:
                del prices[i]
            else:
                i += 1
        
        # new price estimates
        print(f'median: {np.median(prices)} \n mean: {np.mean(prices)} \n 25th percentile: {np.percentile(prices, 25)} \n 10th percentile: {np.percentile(prices, 10)}')
        print(f'min: {np.min(prices)} \n max: {np.max(prices)}')

        return np.percentile(prices, 20) * 0.25
    except Exception as e:
        print(f"An error occurred: {e}")
        quit(1)
    finally:
        browser.quit()