# 🚀 Quick Start - Production Demo

## Prerequisites
- Python 3.11+
- PostgreSQL 15
- Redis (optional)
- Algorand TestNet access

## Installation

```bash
cd f:\AlgoChat_Pay

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

## Pre-Demo Setup (5 minutes)

### 1. Run Demo Mode Script
```bash
python scripts/demo_mode.py
```

This will:
- ✅ Verify Algorand connection
- ✅ Create 4 demo wallets
- ✅ Check balances
- ✅ Generate demo script

### 2. Fund Wallets (if needed)
If any wallets show "LOW", fund them:
1. Go to: https://bank.testnet.algorand.network/
2. Paste wallet address
3. Click "Dispense"
4. Wait 5 seconds

### 3. Start Services

```bash
# Terminal 1: Start PostgreSQL (if not running)
# (Usually auto-starts on Windows)

# Terminal 2: Start Redis (optional)
redis-server

# Terminal 3: Start Backend
uvicorn backend.main:app --reload --port 8000
```

### 4. Verify System Health
```bash
curl http://localhost:8000/health/all
```

Should return:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy", ...},
    "algorand": {"status": "healthy", ...}
  }
}
```

## Demo Flow (7 minutes)

### Opening (30 seconds)
"**AlgoChat Pay** - A campus wallet on WhatsApp, powered by Algorand blockchain"

### 1. Wallet Creation (30 seconds)
**Show:** Alice texts `balance`
**Result:** Wallet created instantly, address shown

**Talking Point:** "Custodial wallet with AES-256 encryption for ease of use"

### 2. Send Payment (1 minute)
**Show:** Alice texts `send +14155552002 5`
**Result:** Payment confirmed in ~5 seconds

**Talking Point:** 
- "Algorand's 4.5-second finality"
- "Automatic retry with node fallback"
- Show AlgoExplorer link

### 3. Bill Splitting (1.5 minutes)
**Show:** Alice texts `split 30 +14155552002 +14155552003 dinner`
**Result:** PyTeal smart contract splits bill 3 ways (10 ALGO each)

**Talking Point:**
- "Smart contract ensures fairness"
- "WhatsApp notifications to all participants"

### 4. Fundraising (1.5 minutes)
**Show:** Organizer texts `fund create 100 Help Campus Food Bank`
**Result:** Campaign created with ID

**Show:** Alice texts `contribute 20 to fund 1`
**Result:** Progress bar updates (20/100 = 20%)

**Talking Point:** "Transparent fundraising with blockchain audit trail"

### 5. NFT Tickets (1 minute)
**Show:** Alice texts `ticket buy TechFest 5`
**Result:** NFT ticket minted, unique ticket number

**Talking Point:**
- "NFTs prevent ticket scalping"
- "Stored as Algorand Standard Asset"

### 6. Admin Dashboard (1 minute)
**Show:** Open `http://localhost:8000/admin/dashboard`

**Metrics to highlight:**
- Total transactions
- Transaction success rate
- Total volume in ALGO
- Active fundraising campaigns

**Talking Point:** "Production-ready observability and monitoring"

### Closing (30 seconds)
"Built for production with:
- ✅ Auto-retry and node fallback
- ✅ Rate limiting and security
- ✅ Health checks and metrics
- ✅ Integration tests"

## Key Endpoints for Demo

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Algorand health
curl http://localhost:8000/health/algorand

# All systems
curl http://localhost:8000/health/all
```

### Metrics
```bash
# System overview
curl http://localhost:8000/metrics

# Performance stats
curl http://localhost:8000/metrics/performance
```

### Admin Dashboard
```bash
# Dashboard stats
curl http://localhost:8000/admin/dashboard

# List users
curl http://localhost:8000/admin/users

# User details
curl http://localhost:8000/admin/users/+14155552001

# Fundraising campaigns
curl http://localhost:8000/admin/funds

# Audit logs
curl http://localhost:8000/admin/audit-logs
```

## Troubleshooting

### Issue: "Cannot connect to Algorand"
**Solution:** Check primary node:
```python
from algosdk.v2client import algod
client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
print(client.status())
```

### Issue: "Insufficient balance"
**Solution:** Fund wallet at https://bank.testnet.algorand.network/

### Issue: "Rate limit exceeded"
**Solution:** Wait 60 seconds or adjust in `backend/config.py`:
```python
RATE_LIMIT_PER_MINUTE: int = 100  # Increase for demo
```

### Issue: "Database connection failed"
**Solution:** 
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Run: `python -c "from backend.database import engine; engine.connect()"`

## Demo Script (Copy-Paste Ready)

### Alice's Phone (+14155552001)
```
balance
send +14155552002 5
split 30 +14155552002 +14155552003 dinner
contribute 20 to fund 1
ticket buy TechFest 5
history
```

### Bob's Phone (+14155552002)
```
balance
history
```

### Charlie's Phone (+14155552003)
```
balance
```

### Organizer's Phone (+14155552004)
```
fund create 100 Help Campus Food Bank
```

## Judge Q&A - Prepared Answers

### Q: "How do you handle Algorand node failures?"
**A:** "We implemented automatic fallback to backup nodes (Nodely, PureStake) with circuit breaker pattern. Failed transactions retry with exponential backoff."

### Q: "What about security?"
**A:** "Rate limiting (10 req/min), command injection detection, transaction limits (100 ALGO/tx, 500 ALGO/day), audit logging, and AES-256 key encryption."

### Q: "How do you ensure reliability during live demo?"
**A:** "Retry logic with 3 attempts, node fallback, demo mode script with pre-funded wallets, and comprehensive health checks."

### Q: "Is this production-ready?"
**A:** "Yes - structured logging with correlation IDs, health checks, metrics, integration tests, admin dashboard, and queue-based async processing."

### Q: "How does this scale?"
**A:** "Connection pooling, Redis caching, batch processing utilities, and async transaction queue with dead letter queue for failed operations."

## Emergency Backup Plan

If live WhatsApp fails:
1. Show pre-recorded video
2. Use curl to hit backend API directly
3. Show admin dashboard with pre-populated data

If Algorand TestNet is down:
1. Explain auto-fallback to backup nodes
2. Show health check detecting issue
3. Demonstrate retry logic in code

If database fails:
1. Show SQLite fallback option
2. Explain high availability setup
3. Show health check reporting degraded state

## Post-Demo

### Show Code Quality
```bash
# Run tests
pytest tests/ -v

# Show test coverage
pytest --cov=backend tests/
```

### Show Logs
```bash
# Structured logs
tail -f logs/algochat.log | jq .
```

### Show Monitoring
Open admin dashboard and show:
- Real-time transaction count
- Success rate
- Average confirmation time

---

## 🎯 Success Criteria

Demo is successful if you show:
- ✅ Instant wallet creation
- ✅ Fast payment (~5 seconds)
- ✅ Smart contract (bill split)
- ✅ NFT ticket minting
- ✅ Admin dashboard
- ✅ Health checks
- ✅ Error handling (intentionally trigger, show retry)

**Good luck! You've got this! 🚀**
