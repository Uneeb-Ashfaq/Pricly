from flask import Flask, render_template, request, url_for, redirect  
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Prevents warning
db = SQLAlchemy(app)

class Product(db.Model):  #database model
    id = db.Column(db.Integer, primary_key=True) 
    url = db.Column(db.String(500), nullable=False) 
    image_url = db.Column(db.String(500))
    name = db.Column(db.String(100)) 
    current_price = db.Column(db.Float) 
    target_price = db.Column(db.Float, nullable=False)  
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    message_sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
            return f'<Product {self.url}>' 
    



# Homepage - shows products
@app.route('/', methods=['POST', 'GET']) 
def index():
    if request.method == 'POST': 
        product_url = request.form.get('product_url')  #getting url from form
        target_price_input = request.form.get('target_price')
        target_price = float(target_price_input)

        try: #scraping the product details
            name, current_price, image_url= scrape(product_url)
            current_price = float(re.search(r"\d+(?:\.\d+)?", current_price.replace(",", "")).group())

            
            #current_price = float(current_price.replace('$', '').replace('Now ', '').replace(',', '').replace('US','').replace("CAD","").replace('CA', '').replace('Sale price', '').strip()) 
        except Exception as e: #handling scraping errors
            return f"There was an issue scraping the product: {str(e)}"
        new_product = Product( #adding product to database
            image_url=image_url, 
            url=product_url,
            name=name,
            current_price=current_price,
            target_price=target_price,
            date_added=datetime.now(),
        )        
        try : #committing to database
            db.session.add(new_product) 
            db.session.commit()
            return redirect(url_for('index')) #redirecting to homepage
        except:
            return "There was an issue adding your product" #handling database errors
    else:
        products = Product.query.order_by(Product.date_added).all() #fetching all products from database
        return render_template('index.html', products=products) #rendering homepage with products




@app.route('/delete/<int:id>') #delete product
def delete(id):
    product_to_delete = Product.query.get_or_404(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that product"

def scrape(url): #scraping function
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
    elif "steampowered.com" in url:
        name_element = soup.find("div", id="appHubAppName")
        price_element = soup.find("div", class_="game_purchase_price")
        image_element = soup.find("img", class_="game_header_image_full")

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



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)



'''

 #elif "amazon.com" in url or "amazon.ca" in url: #does not work at the momennt
        #name_element = soup.find("h1", id="title")
        #price_element = soup.find("span", class_="a-price-whole") 
        #image_element = soup.find(id="landingImage")
    #elif "etsy.com" in url or "etsy.ca" in url: #does not work at the momennt
        #name_element = soup.find("h1", class_="wt-line-height-tight wt-break-word wt-text-body")
        #price_element = soup.find("p", class_="wt-text-title-larger wt-mr-xs-1 wt-text-black")
        #image_element = soup.find("img", class_="wt-max-width-full wt-horizontal-center wt-vertical-center carousel-image wt-rounded")
    #elif "sephora.com" in url or "sephora.ca" in url: #does not work at the momennt
        #name_element = soup.find("h1")
        #price_element = soup.find("b")
        #image_element = soup.find("img")
    #elif "bestbuy.com" in url:
        #name_element = soup.find("h1", class_="h4")
        #price_element = soup.find("span", class_="text-default")
        #image_element = soup.find("img", class_="object-contain")
   # elif "lowes.com" in url or "lowes.ca" in url: #Does Not Work!
       # name_element = soup.find("h1",class_="product-brand-description")
       # price_element = soup.find("div").find("Price")
       # image_element = soup.find("img", class_="tile-img")
#    
 elif "costco.com" in url or "costco.ca" in url: # Does not Work 
        name_element = soup.find("h1", class_="product-title")
        price_element = soup.find("span", class_="value")
        image_element = soup.find("img", id="heroImage_zoom")


    elif "target.com" in url or "target.ca" in url:  #Only Price not working atm
        name_element = soup.find("h1",id="pdp-product-title-id")
        price_element = soup.find("div", class_="styles_currentPriceFontSize__Xps20")
        image_element = soup.find("img")

    
    elif "lenovo.com" in url or "lenovo.ca" in url:
        name_element = soup.find("h1",class_="product_summary")
        price_element = soup.find("span", class_="price-title")
        image_element = soup.find("img", tabindex="0")

        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
 '''