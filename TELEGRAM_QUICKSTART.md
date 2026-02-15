# 🚀 Telegram Bot Quick Start

## Essential Steps (5 minutes)

### 1️⃣ Create Bot (2 min)
1. Open Telegram → Search `@BotFather`
2. Type: `/newbot`
3. Name: `AlgoChat Pay Bot`
4. Username: `algochat_pay_bot` (must end in 'bot')
5. Copy token: `1234567890:AAE_xxx...`

### 2️⃣ Configure Token (1 min)
Edit `.env` file:
```bash
TELEGRAM_BOT_TOKEN=1234567890:AAE_xxxxxxxxxxxxxxxxxxxxx
```

### 3️⃣ Start Backend (1 min)
```powershell
# Terminal 1: Start backend
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload

# Terminal 2: Start ngrok (if not running)
ngrok http 8000
```

### 4️⃣ Set Webhook (1 min)
```powershell
# Run automated setup
.\setup_telegram.ps1

# Enter your ngrok URL when prompted:
# https://abc123.ngrok-free.app
```

### 5️⃣ Test Bot (30 sec)
1. Open Telegram
2. Search: `@algochat_pay_bot`
3. Click **Start**
4. Type: `/register +1234567890`
5. Type: `balance`

✅ **Done!** Bot is live.

---

## Manual Webhook Setup (Alternative)

If automated script fails, use browser:

1. Get ngrok URL: `https://abc123.ngrok-free.app`
2. Open in browser:
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://abc123.ngrok-free.app/webhook/telegram
```
3. Should see: `{"ok":true,"result":true}`

---

## Test Commands

```
/start          - Welcome message
/register +1234567890  - Register phone
balance         - Check ALGO balance
help            - Show all commands
history         - Transaction history
pay 10 ALGO to +1234567890  - Send payment
```

---

## Architecture

```
Telegram → Bot API → ngrok → FastAPI → Shared Bot Logic → Algorand
WhatsApp → Twilio  → ngrok → FastAPI → Shared Bot Logic → Algorand
```

Both platforms use the **same** command parser and services!

---

## Troubleshooting

### Bot not responding?
```powershell
# Check webhook status
$token = "YOUR_TOKEN"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"
```

### Webhook URL changed?
```powershell
# Re-run setup script
.\setup_telegram.ps1
```

### Backend not seeing requests?
- Check ngrok: http://localhost:4040
- Check logs: `Get-Content logs/algochat.log -Tail 50`
- Test endpoint: `curl http://localhost:8000/webhook/telegram`

---

## Files Created

✅ `bot/telegram_webhook.py` - Telegram handler  
✅ `TELEGRAM_SETUP.md` - Full documentation  
✅ `setup_telegram.ps1` - Automated setup script  
✅ `backend/main.py` - Updated with Telegram router  
✅ `backend/config.py` - Added Telegram settings  
✅ `.env` - Added TELEGRAM_BOT_TOKEN  

---

## Production Deployment

For production (not ngrok):

1. Deploy to **Render/Railway/Heroku**
2. Get production URL: `https://yourapp.onrender.com`
3. Set webhook with production URL:
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://yourapp.onrender.com/webhook/telegram
```

---

📖 **Full Guide:** [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)
