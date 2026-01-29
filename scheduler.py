import schedule
import time
from run_alerts import check_prices, send_price_alerts


def job():
    print("⏰ Job started")
    check_prices()
    send_price_alerts()
    print("✅ Job finished")

print("🚀 Scheduler started...")
# Run every day at 8 AM
schedule.every().day.at("08:00").do(job)

# this check if it is time to do the job (press (Ctrl+C) to stop)
while True:
    schedule.run_pending()
    time.sleep(30)
