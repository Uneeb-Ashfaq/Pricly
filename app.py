from flask import Flask, render_template, request, url_for, redirect  
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Prevents warning
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    target_price = db.Column(db.Float) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
            return f'<Product {self.name}>'


# Homepage - shows products
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        product_url = request.form.get('product_url')  
        target_price = request.form.get('target_price')
        new_product = Product( url=product_url,target_price=target_price, date_added=datetime.now())
        try :
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return "There was an issue adding your product"
    else:
        products = Product.query.order_by(Product.date_added).all()
        return render_template('index.html', products=products)




@app.route('/delete/<int:id>')
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
