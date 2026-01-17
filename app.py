from flask import Flask, render_template, request, url_for, redirect  
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from scraper import scrape  # ADD THIS LINE





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