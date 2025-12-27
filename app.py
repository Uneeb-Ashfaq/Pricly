from flask import Flask, render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
            return f'<Product {self.name}>'

@app.route('/')

def index():
    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
