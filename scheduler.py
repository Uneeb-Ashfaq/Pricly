import schedule
import time
from alerts import check_prices, send_price_alerts


def job():
    check_prices()
    send_price_alerts()

# Run every day at 8 AM
schedule.every().day.at("08:00").do(job)

# this check if it is time to do the job (press (Ctrl+C) to stop)
while True:
    schedule.run_pending()
    time.sleep(60)  