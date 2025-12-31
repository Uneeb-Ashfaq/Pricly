from twilio.rest import Client
import alerts.keys as keys

client = Client(keys.ACCOUNT_SID, keys.AUTH_TOKEN)

message = client.messages.create(
    body="Hello from Twilio!",
    from_=keys.TWILIO_NUMBER,
    to=keys.MY_NUMBER
)
print(f"Message sent with SID: {message.sid}")