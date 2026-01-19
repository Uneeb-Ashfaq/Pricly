from flask import Flask, render_template, request, url_for, redirect  
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from scraper import scrape  





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


