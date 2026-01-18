from bs4 import BeautifulSoup
import requests
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def scrape(url):
    selenium_sites = ['phantom']
    if any(site in url for site in selenium_sites):
        return scrape_selenium(url)
    else:
        return scrape_beautifulsoup(url)








def scrape_beautifulsoup(url): #scraping function


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',

        #these are mainly for walmart atm
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',


      
    }

    time.sleep(2)  # Wait 1 second before making request
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Raise error for bad status codes
    soup = BeautifulSoup(response.text, 'html.parser')
    if "walmart.com" in url or "walmart.ca" in url: # Works!
        name_element = soup.find("h1", itemprop="name")
        price_element = soup.find("span", itemprop="price")
        image_element = soup.find("img", {"loading": "eager"})
    elif "newegg.com" in url or "newegg.ca" in url: #Slight problem to check later
        name_element = soup.find("h1",class_="product-title")
        price_element = soup.find("div", class_="price-current").find("strong")
        image_element = soup.find("img", class_="product-view-img-original")
    elif "ebay.com" in url or "ebay.ca" in url: #Works!
        name_element = soup.find("h1", class_="x-item-title__mainTitle")
        price_element = soup.find("div", class_="x-price-primary")
        image_element = soup.find("img")
    elif "nike.com" in url or "nike.ca" in url: # WORKS!
        name_element = soup.find("h1", id="pdp_product_title")  
        price_element = soup.find("span",attrs={"data-testid": "currentPrice-container"}) 
        image_element = soup.find("img")
    elif "jcpenney.com" in url or "jcpenney.ca" in url: #price not working yet
        name_element = soup.find("h1",id="productTitle-false") 
        price_element = soup.find("span", attrs={"data-automation-id": "at-price-value"})
        print(price_element)
        image_element = soup.find("img")
    elif "apple.com" in url or "apple.ca" in url: # error (Picture doesnt work)!
        name_element = soup.find("h1")
        price_element = soup.find("span", class_="rc-price")
        image_element = soup.find("img", class_="rf-configuration-hero-image") 
    elif "puma.com" in url or "puma.ca" in url:  
        name_element = soup.find("h1")
        price_element = soup.find("span", attrs={"data-test-id": "item-sale-price-pdp"}) or soup.find("span", attrs={"data-test-id": "item-price-pdp"})
        image_element = soup.find("img")
    elif "berluti.com" in url:  # Works!
        name_element = soup.find("h1")
        price_element = soup.find("div", class_="prices")
        image_element = soup.find("img", class_="pdp-image ph-45")
    elif "ae.com" in url or "ae.ca" in url: #works
        name_element = soup.find("h1")
        price_element = soup.find("div", attrs={"data-testid": "sale-price"}) or soup.find("div", attrs={"data-testid": "list-price"})
        image_element = soup.find("img")
    elif "forever21" in url: #works
        name_element = soup.find("h1")
        price_element = soup.find("sale-price")
        image_element = soup.find("img", {"loading": "eager"})
    elif "dell" in url: #works
        name_element = soup.find("span", class_="page-title font-weight-md")
        price_element = soup.find("span", attrs={"data-bind": "html: salePrice"}) or soup.find("span", attrs={"data-bind": "html: marketPrice"})
        image_element = soup.find("img", attrs={"data-testid": "sharedPolarisHeroPdImage"})
    elif "goodminds" in url: #works
        name_element = soup.find("h1")
        price_element = soup.find("Span", class_="price") or soup.find("div", class_="price-list")
        image_element = soup.find("img", class_="product-gallery__image")
    elif "bananarepublic" in url: #WORKS 
        name_element = soup.find("h1")
        price_element = soup.find("span", class_="current-sale-price")
        image_element = soup.find("img", {"fetchpriority": "high"})
    elif "steampowered.com" in url: #Works
        name_element = soup.find("div", id="appHubAppName")
        price_element = soup.find("div", class_="game_purchase_price")
        image_element = soup.find("img", class_="game_header_image_full")
    elif "crunchyroll.com" in url: #Works
        name_element = soup.find("h2")
        price_element = soup.find("b")
        image_element = soup.find("img", )
    elif "oldnavy" in url: #Works
        name_element = soup.find("h1", class_="pdp-product-title")
        price_element = soup.find("span", class_="current-sale-price")
        image_element = soup.find("img")

    


    else:
        raise Exception("Website not supported for scraping.")

    name = name_element.get_text().strip() if name_element else "Unknown Product"
    current_price = price_element.get_text().strip() if price_element else "0.00"
    image_url =  image_element.get('data-srcset') or image_element.get('data-src')  or image_element.get('src')    if image_element else None
    if '{width}' in image_url:
        image_url = image_url.replace('{width}', '500') # this is for goodminds
    if image_url.startswith('/') and ('bananarepublic' in url):
        image_url = 'https://bananarepublic.gap.com' + image_url # special case
 

    #print('THIS IS THE IMAGE URL: ', image_url)
    #print(response.text[:2500])  # Debugging line to check HTML content       

    return name, current_price, image_url

#Scrapes JavaScript-heavy sites with Selenium
def scrape_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        
        if "phantom" in url:
            name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="token-page-fungible-name"]'))
            ).text
            
            price = driver.find_element(By.CSS_SELECTOR, '[data-testid="token-page-fungible-price"]').text
            image = driver.find_element(By.TAG_NAME, 'img').get_attribute('src')
        
        
        else:
            driver.quit()
            return None, None, None
        
        driver.quit()
        return name, price, image
    
    except Exception as e:
        driver.quit()
        raise Exception(f"Selenium scraping failed: {str(e)}")


