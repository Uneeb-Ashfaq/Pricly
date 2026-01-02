from twilio.rest import Client
import alerts.keys as keys
from app import app, db, Product, scrape

def check_prices():
    with app.app_context():
        try:
            for product in Product.query.all():
                name, price, image_url = scrape(product.url)
                price = float(price.replace('$', '').replace('Now ', '').replace(',', '').replace('CA', '').strip().replace('US','')) 
                product.current_price = price
            db.session.commit()
        except Exception as e:
            print(f"Error checking prices: {str(e)}")

client = Client(keys.ACCOUNT_SID, keys.AUTH_TOKEN)
def send_price_alerts():
    with app.app_context():
        for product in Product.query.all():
            if product.current_price <= product.target_price and not product.message_sent:
                try:
        
                    message = client.messages.create(
                        body=(f"Your target price for {product.name} has been reached!\n" 
                            f"Current price: ${product.current_price}.\n"
                            f"Check it out here: {product.url}"),
                        from_=keys.TWILIO_NUMBER,
                        to=keys.MY_NUMBER)  
                    
                    product.message_sent = True
                    db.session.commit()
                
                    print(f"Message sent with SID: {message.sid}")
                except Exception as e:
                    print(f"Error sending message: {e}")