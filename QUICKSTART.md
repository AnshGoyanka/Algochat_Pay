# 🚀 AlgoChat Pay - Quick Reference Guide

## ⚡ 5-Minute Setup

### Step 1: Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Generate encryption key
python -c "from backend.security.encryption import EncryptionService; print(EncryptionService.generate_encryption_key())"

# Add to .env:
# ENCRYPTION_KEY=<generated-key>
```

### Step 2: Configure Twilio
1. Sign up: https://www.twilio.com/try-twilio
2. Get WhatsApp Sandbox: Console → Messaging → Try it out → Try WhatsApp
3. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

### Step 3: Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Quick start (initializes DB + starts server)
python start.py

# OR manual steps:
python -c "from backend.database import init_db; init_db()"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Expose Webhook (Development)
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Copy HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Step 5: Configure Twilio Webhook
1. Go to: Twilio Console → Messaging → Settings → WhatsApp Sandbox
2. Set "When a message comes in": `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
3. Method: POST
4. Save

### Step 6: Test!
Send to your Twilio WhatsApp number:
```
balance
```

You should get a welcome message with your new wallet! 🎉

---

## 📱 Command Cheat Sheet

```
┌─────────────────────────────────────────────────────────┐
│  WALLET COMMANDS                                        │
├─────────────────────────────────────────────────────────┤
│  balance              Check your ALGO balance           │
│  history              View transaction history          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PAYMENT COMMANDS                                       │
├─────────────────────────────────────────────────────────┤
│  pay 50 ALGO to +91XXXXXXXXXX                          │
│  send 25 ALGO to +91XXXXXXXXXX                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BILL SPLITTING                                         │
├─────────────────────────────────────────────────────────┤
│  split 400 ALGO dinner with +91XXX +91YYY              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  EVENT TICKETS                                          │
├─────────────────────────────────────────────────────────┤
│  buy ticket TechFest                                    │
│  my tickets                                             │
│  verify ticket TIX-ABC123                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  FUNDRAISING                                            │
├─────────────────────────────────────────────────────────┤
│  create fund Trip goal 500 ALGO                         │
│  contribute 50 ALGO to fund 1                           │
│  view fund 1                                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  HELP                                                   │
├─────────────────────────────────────────────────────────┤
│  help                 Show all commands                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Flow

### 1. Create Test Wallets
```bash
python scripts/create_test_wallets.py
```
Creates 5 test wallets in database.

### 2. Fund Wallets
**Option A: TestNet Dispenser**
- Visit: https://bank.testnet.algorand.network/
- Paste each wallet address
- Get 10 ALGO per wallet

**Option B: Script (if you have funded account)**
```bash
python scripts/fund_wallets.py
```

### 3. Test Scenarios

**Scenario 1: First User**
```
Message: balance
Expected: Welcome message with new wallet
```

**Scenario 2: Payment**
```
Message: pay 2 ALGO to +919876543211
Expected: ✅ Payment Sent! (4.5 sec confirmation)
```

**Scenario 3: Bill Split**
```
Message: split 300 ALGO dinner with +91XXX +91YYY
Expected: Bill split details (100 ALGO each)
```

**Scenario 4: Ticket Purchase**
```
Message: buy ticket TechFest
Expected: 🎫 Ticket Purchased! (NFT details)
```

**Scenario 5: Fundraising**
```
Message: create fund Trip goal 500 ALGO
Expected: 🎯 Campaign Created! (Fund ID)

Message: contribute 50 ALGO to fund 1
Expected: 🎉 Contribution Recorded!
```

---

## 🔧 Common Issues & Solutions

### Issue: "Database connection failed"
**Solution:**
```bash
# Check PostgreSQL is running
docker-compose up postgres -d

# Or install locally:
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
```

### Issue: "Invalid encryption key"
**Solution:**
```bash
# Generate new key
python -c "from backend.security.encryption import EncryptionService; print(EncryptionService.generate_encryption_key())"

# Add to .env
ENCRYPTION_KEY=<generated-key>
```

### Issue: "Twilio webhook not receiving messages"
**Solution:**
1. Check ngrok is running: `ngrok http 8000`
2. Update Twilio webhook URL with new ngrok URL
3. Ensure webhook URL ends with `/webhook/whatsapp`
4. Check server logs: `tail -f logs/algochat.log`

### Issue: "Insufficient balance"
**Solution:**
```bash
# Fund wallet from TestNet dispenser
# https://bank.testnet.algorand.network/

# Check balance
curl http://localhost:8000/api/v1/wallet/balance?phone=+91XXXXXXXXXX
```

---

## 📊 Monitoring

### Check Server Status
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Real-time logs
tail -f logs/algochat.log

# Docker logs
docker-compose logs -f backend
```

### Database Queries
```bash
# Connect to database
docker exec -it algochat_db psql -U algochat -d algochat_db

# List users
SELECT phone_number, wallet_address, created_at FROM users;

# List transactions
SELECT tx_id, sender_phone, amount, status FROM transactions ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎬 Demo Mode

### Prepare Demo
```bash
# 1. Create test wallets
python scripts/create_test_wallets.py

# 2. Fund wallets (10 ALGO each)
python scripts/fund_wallets.py

# 3. Deploy smart contracts
cd smart_contracts
python deploy.py

# 4. Start server
python start.py

# 5. Start ngrok
ngrok http 8000
```

### Demo Script (7 minutes)
1. **Intro (30 sec)**: Explain problem - campus payment fragmentation
2. **Wallet Creation (1 min)**: Send "balance" → instant wallet
3. **Payment (1.5 min)**: Pay friend 2 ALGO → 4.5 sec confirmation
4. **Bill Split (2 min)**: Split 300 ALGO dinner → equal distribution
5. **Ticket NFT (1.5 min)**: Buy TechFest ticket → unique NFT
6. **Fundraising (30 sec)**: Create fund + contribute → transparency

**Key Stats to Highlight:**
- ⚡ 4.5 second finality (vs 30+ min traditional)
- 💰 0.001 ALGO fees = ₹0.10 (vs ₹10)
- 🔒 NFT tickets = 0 fakes
- 📊 100% fundraising transparency

---

## 🏗️ Project Structure Quick Nav

```
algochat-pay/
├── backend/main.py           ← FastAPI entry point
├── bot/whatsapp_webhook.py   ← WhatsApp message handler
├── smart_contracts/deploy.py ← Deploy contracts
├── scripts/create_test_wallets.py ← Testing setup
├── start.py                  ← Quick start script
└── README.md                 ← Full documentation
```

---

## 🆘 Support

**Documentation**: See [README.md](README.md) for comprehensive guide  
**Architecture**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for file details  
**API Docs**: http://localhost:8000/docs (when running)  

**Troubleshooting Steps:**
1. Check logs: `logs/algochat.log`
2. Verify environment: `.env` file configured
3. Test endpoints: `curl http://localhost:8000/health`
4. Check database: `docker-compose ps`

---

## 🎯 Hackathon Submission Checklist

- [x] Working demo on TestNet
- [x] WhatsApp bot responding to commands
- [x] Smart contracts deployed
- [x] Database storing wallet mappings
- [x] Security implemented (AES encryption)
- [x] Code documented
- [x] README with setup instructions
- [x] Docker deployment ready
- [ ] Record demo video
- [ ] Prepare pitch deck
- [ ] Test all features before demo

---

**Built for Hackspiration - Track 1: Future of Finance**  
**Team Xion | Campus Wallet on WhatsApp**
