import requests
from bs4 import BeautifulSoup

'''
Scrapes a given url for a price in USD.
'''
def scraper(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    price = soup.find('span', {'class': 'a-price-whole'}).text
    return price

print(scraper('https://www.amazon.com/Crayola-Crayons-Non-Toxic-Coloring-Supplies/dp/B017MIRU96'))