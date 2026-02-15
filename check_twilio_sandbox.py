"""
Quick script to check Twilio sandbox settings
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

print("=" * 60)
print("TWILIO WHATSAPP SANDBOX INFO")
print("=" * 60)
print(f"\nAccount SID: {account_sid}")
print(f"WhatsApp Number: +14155238886")
print("\n📱 TO RECEIVE NOTIFICATIONS, YOUR FRIEND MUST:")
print("-" * 60)
print("1. Open WhatsApp")
print("2. Add contact: +1 (415) 523-8886")
print("3. Send this message:")
print("\n   👉 Check your Twilio Console for the join code")
print("\n   Example: join <your-sandbox-word>")
print("\n4. Wait for confirmation from Twilio")
print("-" * 60)
print("\n🔗 Get your join code here:")
print("https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
print("\n" + "=" * 60)
