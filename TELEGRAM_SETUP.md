# 🤖 Telegram Bot Setup Guide for AlgoChat Pay

Complete guide to integrate Telegram bot alongside your existing WhatsApp bot.

---

## 📋 Table of Contents

1. [Create Telegram Bot](#step-1--create-telegram-bot)
2. [Configure Environment](#step-2--configure-environment)
3. [Set Telegram Webhook](#step-3--set-telegram-webhook)
4. [Start the Server](#step-4--start-the-server)
5. [Test Your Bot](#step-5--test-your-bot)
6. [Architecture Overview](#architecture-overview)
7. [Troubleshooting](#troubleshooting)

---

## 🟦 Step 1 — Create a Telegram Bot

### Inside Telegram App:

1. **Open Telegram** (mobile or desktop)

2. **Search for** [@BotFather](https://t.me/botfather)

3. **Start the chat** and type:
   ```
   /newbot
   ```

4. **Follow the prompts:**
   - Give your bot a **name** (e.g., `AlgoChat Pay Bot`)
   - Give your bot a **username** (must end in `bot`)
     - Example: `algochat_pay_bot` or `my_campus_wallet_bot`

5. **Save your token:**
   
   After creation, BotFather will give you a token like:
   ```
   1234567890:AAE_xxxxxxxxxxxxxxxxxxxxx
   ```
   
   ⚠️ **Keep this secret!** Anyone with this token can control your bot.

### Example Conversation:

```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it?

You: AlgoChat Pay Bot
BotFather: Good. Now let's choose a username for your bot.

You: algochat_pay_bot
BotFather: Done! Congratulations on your new bot.

Token: 1234567890:AAE_xxxxxxxxxxxxxxxxxxxxx

You can now add a description, about section and profile picture for your bot.
```

---

## 🟦 Step 2 — Configure Environment

### 1. Open your `.env` file

Located at: `f:\AlgoChat_Pay\.env`

### 2. Replace the Telegram token placeholder:

Find this line:
```bash
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
```

Replace with your actual token:
```bash
TELEGRAM_BOT_TOKEN=1234567890:AAE_xxxxxxxxxxxxxxxxxxxxx
```

### 3. Update the webhook URL (we'll do this after ngrok is running)

For now, leave it as:
```bash
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook/telegram
```

### Complete .env Example:

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_WEBHOOK_URL=https://your-domain.com/webhook/whatsapp

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/webhook/telegram
```

---

## 🟦 Step 3 — Set Telegram Webhook

### Option A: Automated Setup (Recommended)

We'll create a PowerShell script to automate this:

#### 1. Create `setup_telegram.ps1`:

```powershell
# Get the bot token from .env
$envContent = Get-Content .env
$botToken = ($envContent | Select-String "TELEGRAM_BOT_TOKEN=(.+)").Matches.Groups[1].Value

# Get ngrok URL (you should have this running)
Write-Host "📡 Enter your ngrok URL (e.g., https://abc123.ngrok-free.app):"
$ngrokUrl = Read-Host

# Construct webhook URL
$webhookUrl = "$ngrokUrl/webhook/telegram"

# Set webhook
$apiUrl = "https://api.telegram.org/bot$botToken/setWebhook?url=$webhookUrl"

Write-Host "`n🔄 Setting Telegram webhook..."
$response = Invoke-RestMethod -Uri $apiUrl -Method Get

if ($response.ok) {
    Write-Host "✅ Telegram webhook set successfully!" -ForegroundColor Green
    Write-Host "📍 Webhook URL: $webhookUrl" -ForegroundColor Cyan
    
    # Update .env file
    $envContent = $envContent -replace "TELEGRAM_WEBHOOK_URL=.+", "TELEGRAM_WEBHOOK_URL=$webhookUrl"
    $envContent | Set-Content .env
    Write-Host "✅ Updated .env file" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to set webhook" -ForegroundColor Red
    Write-Host $response
}

# Get webhook info
Write-Host "`n📊 Webhook Info:"
$infoUrl = "https://api.telegram.org/bot$botToken/getWebhookInfo"
$info = Invoke-RestMethod -Uri $infoUrl -Method Get
$info.result | Format-List
```

#### 2. Run the script:

```powershell
.\setup_telegram.ps1
```

### Option B: Manual Setup via Browser

1. **Ensure ngrok is running** on your backend:
   ```bash
   ngrok http 8000
   ```

2. **Copy the HTTPS URL** from ngrok (e.g., `https://abc123.ngrok-free.app`)

3. **Open your browser** and navigate to:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://abc123.ngrok-free.app/webhook/telegram
   ```
   
   Replace:
   - `<YOUR_BOT_TOKEN>` with your actual token
   - `abc123.ngrok-free.app` with your ngrok URL

4. **You should see:**
   ```json
   {
     "ok": true,
     "result": true,
     "description": "Webhook was set"
   }
   ```

### Option C: Using curl/PowerShell

```powershell
$token = "YOUR_BOT_TOKEN"
$webhookUrl = "https://abc123.ngrok-free.app/webhook/telegram"

Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/setWebhook?url=$webhookUrl"
```

---

## 🟦 Step 4 — Start the Server

### 1. Activate virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Start the FastAPI backend:

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting AlgoChat Pay
INFO:     Environment: development
INFO:     Algorand Network: testnet
INFO:     Database initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. In another terminal, start ngrok:

```powershell
ngrok http 8000
```

### 4. Verify webhook endpoints:

Visit: http://localhost:8000/docs

You should see both:
- `/webhook/whatsapp` (POST)
- `/webhook/telegram` (POST, GET)

---

## 🟦 Step 5 — Test Your Bot

### Test 1: Basic Connection

1. **Open Telegram**
2. **Search for your bot** by username (e.g., `@algochat_pay_bot`)
3. **Click "Start"** or type `/start`

**Expected Response:**
```
🏦 Welcome to AlgoChat Pay!

To get started, please share your phone number:
1. Click the 📎 attachment button
2. Select 'Contact'
3. Share your contact

Or simply type:
/register +1234567890
```

### Test 2: Register Phone Number

Type:
```
/register +1234567890
```

**Expected Response:**
```
✅ Registered phone: +1234567890

Now you can use all commands!
```

### Test 3: Check Balance

Type:
```
balance
```

**Expected Response:**
```
🏦 AlgoChat Pay Wallet

📱 Phone: +1234567890
💼 Address: ABCD...WXYZ
💰 Balance: 0.0 ALGO

💡 Tip: Send "help" for all commands
```

### Test 4: View Help

Type:
```
help
```

**Expected Response:**
```
🏦 AlgoChat Pay - Command Guide

💰 WALLET COMMANDS
• balance - Check your ALGO balance
• history - View transaction history

💸 PAYMENT COMMANDS
• pay [amount] ALGO to [+phone] - Send ALGO
  Example: pay 10 ALGO to +919876543210

...
```

### Test 5: Check History

Type:
```
history
```

**Expected Response:**
```
📊 Transaction History

No transactions yet.

Send your first payment with:
pay 10 ALGO to +1234567890
```

---

## 🏗️ Architecture Overview

### Dual-Platform Setup

```
┌─────────────┐
│  WhatsApp   │ ─────┐
│   Users     │      │
└─────────────┘      │
                     ▼
              ┌──────────────┐
              │ Twilio API   │
              └──────────────┘
                     │
                     ▼
              ┌──────────────────────┐
              │  ngrok Tunnel        │
              │  (Public HTTPS)      │
              └──────────────────────┘
                     │
┌─────────────┐      │
│  Telegram   │ ─────┤
│   Users     │      │
└─────────────┘      ▼
              ┌──────────────────────┐
              │  FastAPI Backend     │
              │  (localhost:8000)    │
              │                      │
              │  Routers:            │
              │  • /webhook/whatsapp │
              │  • /webhook/telegram │
              └──────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌─────────────┐      ┌─────────────┐
    │  Shared     │      │  Algorand   │
    │  Bot Logic  │      │  TestNet    │
    │             │      │             │
    │ • Parser    │      │ • Payments  │
    │ • Services  │      │ • Wallets   │
    │ • Templates │      │ • NFTs      │
    └─────────────┘      └─────────────┘
```

### Shared Components

Both WhatsApp and Telegram use the **same business logic**:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Command Parser** | `bot/command_parser.py` | Parses user commands |
| **Response Templates** | `bot/response_templates.py` | Formats bot responses |
| **Wallet Service** | `backend/services/wallet_service.py` | Manages Algorand wallets |
| **Payment Service** | `backend/services/payment_service.py` | Processes ALGO transfers |
| **Ticket Service** | `backend/services/ticket_service.py` | NFT ticket operations |
| **Fund Service** | `backend/services/fund_service.py` | Crowdfunding campaigns |

### Key Differences

| Feature | WhatsApp | Telegram |
|---------|----------|----------|
| **Message API** | Twilio TwiML | Telegram Bot API |
| **User ID** | Phone number | Chat ID |
| **Authentication** | Built-in (phone) | Manual registration |
| **Message Format** | XML Response | JSON API Call |
| **Rate Limits** | Twilio limits | Telegram limits (30 msg/sec) |

---

## 🔧 Troubleshooting

### Issue 1: Bot Not Responding

**Symptoms:** You send a message but get no response

**Solutions:**

1. **Check if webhook is set correctly:**
   ```powershell
   $token = "YOUR_BOT_TOKEN"
   Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"
   ```
   
   Should show:
   ```json
   {
     "ok": true,
     "result": {
       "url": "https://abc123.ngrok-free.app/webhook/telegram",
       "has_custom_certificate": false,
       "pending_update_count": 0
     }
   }
   ```

2. **Check backend logs:**
   ```powershell
   # In your terminal running uvicorn, you should see:
   INFO:     Received Telegram update: {...}
   ```

3. **Verify ngrok is running:**
   - Visit http://localhost:4040
   - Check "Requests" tab for incoming POST to `/webhook/telegram`

4. **Test webhook manually:**
   ```powershell
   curl http://localhost:8000/webhook/telegram
   ```
   
   Should return:
   ```json
   {
     "status": "Telegram webhook is active",
     "bot": "AlgoChat Pay"
   }
   ```

### Issue 2: "Webhook not found" Error

**Solution:** ngrok URL changed (happens on free tier restart)

```powershell
# 1. Get new ngrok URL
ngrok http 8000

# 2. Re-run setup script
.\setup_telegram.ps1

# OR manually update webhook:
$token = "YOUR_TOKEN"
$newUrl = "https://NEW_NGROK_URL.ngrok-free.app/webhook/telegram"
Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook?url=$newUrl"
```

### Issue 3: "Unauthorized" Error

**Cause:** Wrong bot token in `.env`

**Solution:**

1. Verify token with BotFather:
   ```
   /mybots → Select your bot → API Token
   ```

2. Update `.env` file

3. Restart uvicorn

### Issue 4: "Phone number required" Loop

**Cause:** User hasn't registered their phone

**Solution:**

User must type:
```
/register +1234567890
```

Or share contact in Telegram:
1. Click 📎 attachment
2. Select "Contact"
3. Choose "My contact"

### Issue 5: Database Connection Error

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection failed
```

**Solution:**

Check your DATABASE_URL in `.env`:
```bash
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx.neon.tech/neondb?sslmode=require
```

Test connection:
```python
python -c "from backend.database import engine; engine.connect(); print('✅ Connected')"
```

### Issue 6: Commands Not Working

**Symptoms:** Bot responds but commands don't execute

**Check:**

1. **Command syntax:**
   ```
   ✅ balance
   ✅ pay 10 ALGO to +1234567890
   ❌ Balance
   ❌ pay 10 algo +1234567890
   ```

2. **View backend logs:**
   ```
   INFO:     Processing Telegram message from chat 123456: balance
   WARNING:  Validation error: Insufficient balance
   ```

3. **Test command parser:**
   ```python
   python -c "
   from bot.command_parser import command_parser
   cmd = command_parser.parse('balance')
   print(cmd.type, cmd.params)
   "
   ```

---

## 🚀 Production Deployment

For production (not ngrok):

### 1. Use a Real Domain

Replace ngrok with:
- **Render.com** (free tier)
- **Railway.app** (free $5 credit)
- **Heroku** (hobby tier)
- **AWS/DigitalOcean** (self-hosted)

### 2. Set Webhook with Production URL

```bash
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://yourdomain.com/webhook/telegram
```

### 3. Enable HTTPS

Telegram **requires** HTTPS for webhooks.

Most hosting providers (Render, Railway) provide this automatically.

### 4. Environment Variables

Set on your hosting platform:
- `TELEGRAM_BOT_TOKEN`
- `DATABASE_URL`
- `ALGORAND_ALGOD_ADDRESS`
- All other vars from `.env`

---

## 📊 Testing Checklist

Before showing to users:

- [ ] Bot responds to `/start`
- [ ] Phone registration works (`/register +phone`)
- [ ] `balance` command creates wallet for new users
- [ ] `help` command shows all commands
- [ ] `history` command shows empty history for new users
- [ ] Backend logs show Telegram updates
- [ ] ngrok dashboard shows POST requests
- [ ] No errors in uvicorn logs
- [ ] Database stores new wallet on first interaction
- [ ] Webhook info shows correct URL
- [ ] Both WhatsApp and Telegram bots work simultaneously

---

## 🎯 Next Steps

### Implement Advanced Features

1. **Persistent Chat ID Mapping:**
   - Create `telegram_users` table
   - Map `chat_id` → `phone_number`
   - Auto-load phone from database

2. **Rich Message Formatting:**
   - Use Telegram's Markdown/HTML
   - Add inline buttons for commands
   - Show QR codes for wallet addresses

3. **Group Chat Support:**
   - Bill splitting in group chats
   - Tag users with `@username`
   - Group fundraising campaigns

4. **Payment Notifications:**
   - Push notifications for received payments
   - Transaction confirmations with blockchain explorer links

5. **Multi-Language:**
   - Detect user language from Telegram
   - Respond in user's language

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   ```powershell
   Get-Content logs/algochat.log -Tail 50
   ```

2. **Test webhook:**
   ```
   http://localhost:4040/inspect/http
   ```

3. **Verify bot token:**
   ```
   https://api.telegram.org/bot<TOKEN>/getMe
   ```

4. **Check Telegram docs:**
   https://core.telegram.org/bots/api

---

## 🎉 Success!

Your AlgoChat Pay bot now supports **both WhatsApp AND Telegram**!

Users can transact on Algorand from either platform using the same backend. 🚀

---

**Built with ❤️ for Algorand Hackathon 2026**
