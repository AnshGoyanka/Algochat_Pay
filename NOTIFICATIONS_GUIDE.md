python test_notifications.pypython test_notifications.py# WhatsApp Notification System 📱

## Overview
AlgoChat Pay now sends real-time WhatsApp notifications for all payment activities! Users will be instantly notified when they receive payments, are added to bill splits, or receive contributions to their fundraisers.

## Features Implemented ✅

### 1. Payment Received Notification
**When it triggers:** Someone sends you ALGO  
**Who gets notified:** The recipient  
**Message includes:**
- Sender's phone number
- Amount received in ALGO
- Payment reference number
- Quick command to check balance

**Example:**
```
🎉 *Payment Received!*

You received *25.50 ALGO* from +919999999999

💰 Payment Ref: P12345

Check balance: /balance
```

### 2. Split Bill Created Notification
**When it triggers:** You're added to a bill split  
**Who gets notified:** All participants in the split  
**Message includes:**
- Who created the split (initiator)
- Your share amount
- Split ID for reference
- Description of the bill
- Quick command to pay your share

**Example:**
```
💸 *Bill Split Request*

+919876543210 added you to a bill split!

📝 Dinner at Italian Restaurant
💰 Your share: 50.00 ALGO
🔖 Split ID: #1

Pay now: /split pay 1
```

### 3. Split Payment Received Notification
**When it triggers:** Someone pays their share of a split you created  
**Who gets notified:** The person who created the split (initiator)  
**Message includes:**
- Who paid
- Amount paid
- Split ID
- Whether everyone has paid or still waiting

**Example:**
```
✅ *Split Payment Received*

+919999888877 paid their share!

💰 Amount: 50.00 ALGO
🔖 Split ID: #1

Status: Waiting for others to pay...

View details: /split status 1
```

### 4. Fund Contribution Notification
**When it triggers:** Someone contributes to your fundraiser  
**Who gets notified:** The fundraiser creator  
**Message includes:**
- Contributor's phone number
- Contribution amount
- Updated total raised
- Progress toward goal
- Progress bar

**Example:**
```
❤️ *New Contribution!*

+919876543210 contributed *100.00 ALGO* to your fundraiser!

📊 Heart Surgery for 8-Year-Old
💰 Total Raised: 350.00 / 600.00 ALGO

Progress: [████████░░░░░░░░] 58%

View fund: /fund 1
```

## Technical Implementation

### Architecture
- **Service:** `backend/services/notification_service.py`
- **Provider:** Twilio WhatsApp Business API
- **Pattern:** Non-blocking (won't fail transactions if notification fails)
- **Error Handling:** Logged warnings for failed notifications

### Integration Points
1. **Payment Service** ([backend/services/payment_service.py](backend/services/payment_service.py))
   - After transaction confirmation
   - Notifies receiver

2. **Split Service** ([backend/services/split_service.py](backend/services/split_service.py))
   - After split creation: Notifies all participants
   - After payment received: Notifies initiator

3. **Fund Service** ([backend/services/fund_service.py](backend/services/fund_service.py))
   - After contribution confirmed
   - Notifies fund creator

### Configuration
Set these environment variables in `.env`:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## Testing

### Run Test Script
```bash
python test_notifications.py
```

This will test all 4 notification types:
1. Payment Received
2. Split Bill Created
3. Split Payment Received
4. Fund Contribution

### Manual Testing
1. **Test Payment:**
   - Send ALGO to another user via WhatsApp bot
   - Receiver should get notification instantly

2. **Test Split Bill:**
   - Create a split: `/split create 100 2 Dinner`
   - Add participants: `/split add <split_id> <phone>`
   - Participants should get notified

3. **Test Split Payment:**
   - Pay your share: `/split pay <split_id>`
   - Initiator should get notification

4. **Test Fund Contribution:**
   - Contribute to a fund: `/fund contribute <fund_id> <amount>`
   - Fund creator should get notification

## Important Notes

### Twilio Sandbox Limitations
- Twilio sandbox requires recipients to opt-in by sending "join <sandbox-word>" first
- For production, you'll need an approved Twilio WhatsApp Business account
- Sandbox is great for testing but has rate limits

### Phone Number Format
- All phone numbers stored with country code (e.g., +918237987667)
- Twilio requires "whatsapp:" prefix (handled automatically)

### Error Handling
- Notification failures **won't** block transactions
- Failed notifications are logged for debugging
- Transactions complete successfully even if notification fails

### Privacy
- Only phone numbers are shared (no wallet addresses in notifications)
- Messages are end-to-end encrypted by WhatsApp
- Notification preferences can be added in future

## Future Enhancements

### Possible Additions:
1. **Notification Preferences**
   - Let users opt-in/opt-out of specific notification types
   - Store preferences in database

2. **Rich Media**
   - Add QR codes for payment links
   - Include fund progress images

3. **Localization**
   - Support multiple languages
   - Detect user's preferred language from profile

4. **Delivery Tracking**
   - Store notification delivery status
   - Retry failed notifications

5. **Email Fallback**
   - Send email if WhatsApp fails
   - Useful for users without WhatsApp

## Troubleshooting

### Notification Not Received?
1. Check Twilio sandbox opt-in (send "join <word>" to sandbox number)
2. Verify phone number format (+<country_code><number>)
3. Check Twilio logs in dashboard
4. Review server logs for errors

### Messages Look Wrong?
- WhatsApp formatting uses *bold* markdown
- Emojis should display correctly
- Line breaks might vary by device

### Rate Limits?
- Twilio sandbox has message limits (~200/day)
- Upgrade to production for higher limits
- Consider batching notifications for bulk operations

## Support
For issues or questions about the notification system:
1. Check Twilio dashboard for API errors
2. Review server logs: `logs/notification_errors.log`
3. Test with the test script: `python test_notifications.py`

---

**Built with:** Twilio WhatsApp Business API  
**Status:** ✅ Fully Integrated  
**Last Updated:** Current conversation session
