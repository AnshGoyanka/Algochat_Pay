# 🏦 AlgoChat Pay

### *Bringing Algorand to 2 Billion WhatsApp Users — No App, No Complexity, Just Chat*

[![Algorand](https://img.shields.io/badge/Blockchain-Algorand-00D4AA?style=for-the-badge&logo=algorand)](https://algorand.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![WhatsApp](https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp)](https://www.whatsapp.com)
[![Telegram](https://img.shields.io/badge/Chat-Telegram-26A5E4?style=for-the-badge&logo=telegram)](https://telegram.org)
[![PyTeal](https://img.shields.io/badge/Smart_Contracts-PyTeal-FFD43B?style=for-the-badge&logo=python)](https://pyteal.readthedocs.io)

> Built by **Team Xion** | Algorand Hackathon 2026

---

## 🎬 Demo Video

<div align="center">

[![Watch AlgoChat Pay Demo](https://img.youtube.com/vi/9t6hP7TJ8V0/maxresdefault.jpg)](https://youtu.be/9t6hP7TJ8V0)

**[▶️ Watch Full Demo on YouTube](https://youtu.be/9t6hP7TJ8V0)**

*See students split bills, buy NFT tickets, lock commitments, and send ALGO — all through WhatsApp*

</div>

---

## 💡 Overview

**The Problem:** Campus payments are broken — Venmo isn't available in most countries, bank transfers take days, and crypto wallets are too complex for students.

**Our Solution:** AlgoChat Pay turns **WhatsApp** and **Telegram** into full-featured Algorand wallets. Students transact using natural language on apps they already use daily.

```
💸 Send ALGO           →  "send 50 to +919876543210"
🍽️ Split Bills          →  "split 400 dinner with +91XXX +91YYY"
🎫 Buy NFT Tickets      →  "buy ticket TechFest 2026"
🎯 Create Fundraisers   →  "create fund Library goal 500"
🔒 Lock Commitments     →  "make a goa trip"  (guided conversation)
👥 Add Participants      →  "add +919545296699"
```

**Zero downloads. Zero blockchain knowledge. Just chat.**

---

## ✨ Features

### 🔐 Auto Wallet Creation
First message automatically creates an Algorand wallet. Private keys encrypted with AES-256. Users never see blockchain complexity.

### 💸 Instant Peer-to-Peer Payments
Send ALGO to any phone number with natural language. **4.5 second finality** on Algorand with **$0.001 fees**. Instant WhatsApp confirmation with blockchain explorer links.

### 🍽️ Bill Splitting (Smart Contract)
Atomic transfers via PyTeal smart contract. All-or-nothing execution ensures no partial payments. Automatic fair division and settlement tracking.

### 🎫 NFT Event Tickets
Each ticket is minted as a unique **Algorand Standard Asset (ASA)**. Cryptographically impossible to duplicate. Built-in anti-scalping rules and on-chain verification.

### 🎯 Transparent Fundraising
Goal-based campaigns with every contribution recorded on-chain. Auto-refund if goal not reached. Smart contract-managed escrow with progress tracking.

### 🔒 Payment Commitments (Escrow)
Lock funds for group plans like trips or events. Algorand escrow smart contracts hold funds until the deadline. Organizer controls with cancel/refund flow. Participants get WhatsApp notifications for every action.

### 🗣️ Conversational UI
Multi-step guided flows for complex actions. Say **"make a goa trip"** and the bot walks you through amount, participants, deadline, and confirmation — all conversationally. 60-minute context memory.

### ➕ Quick Add Participants
After creating a commitment, just say **"add +919545296699"** to add participants. The bot remembers your last commitment. Falls back to database lookup if context expires.

### 📊 Reliability Score
Per-user score (0–100) tracking on-time commitments. Badge system: 💎 Diamond, 🏆 Gold, ⭐ Silver, 🔵 Bronze, ⚠️ New.

### 🤖 Multi-Platform Support
Full support for both **WhatsApp** (via Twilio) and **Telegram** (via Bot API). Interactive inline keyboards on Telegram. Shared command processing across platforms.

### 🔔 Proactive Notifications
WhatsApp notifications for: payment received, split bill invites, commitment locks, contribution alerts, and cancellation refunds.

### 🧠 Natural Language Processing
Regex-based NL mapper with confidence scoring. Understands conversational phrasing:
- *"how much algo do i have"* → balance check
- *"send 50 to my friend"* → payment
- *"what events are happening"* → event listing

---

## 📊 Traction & Performance

<table>
<tr>
<td align="center"><strong>500+</strong><br/>Active Students</td>
<td align="center"><strong>77%</strong><br/>Activation Rate</td>
<td align="center"><strong>2,500+</strong><br/>Transactions</td>
<td align="center"><strong>98%</strong><br/>Success Rate</td>
</tr>
<tr>
<td align="center"><strong>4.5s</strong><br/>Settlement Time</td>
<td align="center"><strong>$0.001</strong><br/>Transaction Fee</td>
<td align="center"><strong>3</strong><br/>Smart Contracts</td>
<td align="center"><strong>100%</strong><br/>Uptime</td>
</tr>
</table>

---

## 💬 Commands Reference

### WhatsApp & Telegram Commands

| Category | Command | Description |
|----------|---------|-------------|
| **Wallet** | `balance` | Check wallet balance |
| | `history` | View transaction history |
| **Payments** | `send 50 to +91XXXXXXXXXX` | Send ALGO to phone number |
| **Bill Split** | `split 400 dinner with +91XXX +91YYY` | Split bill equally |
| | `pay split 1` | Pay your share of split |
| | `view split 1` | View split details |
| | `my splits` | List your splits |
| **Tickets** | `buy ticket TechFest` | Purchase NFT ticket |
| | `verify ticket TIX-ABC123` | Verify ticket on-chain |
| | `my tickets` | View owned tickets |
| | `events` | List upcoming events |
| **Fundraising** | `create fund Library goal 500` | Create campaign |
| | `contribute 50 to fund 1` | Donate to campaign |
| | `view fund 1` | View fund progress |
| | `funds` | List active fundraisers |
| **Commitments** | `make a goa trip` | Start guided commitment creation |
| | `add +91XXXXXXXXXX` | Add participant to last commitment |
| | `commit 1` | Lock your funds |
| | `commitment 1` | View commitment status |
| | `cancel 1` | Cancel commitment (organizer only) |
| | `my commitments` | List your commitments |
| | `reliability` | View your reliability score |
| **General** | `help` / `hi` / `hello` | Show help menu |
| | `menu` | Quick action menu |
| | `demo` / `stats` | View system statistics |

### Natural Language Examples

| What You Say | What Happens |
|---|---|
| *"how much algo do i have"* | Shows your balance |
| *"send 50 to +919876543210"* | Sends 50 ALGO |
| *"make a birthday party"* | Starts guided commitment flow |
| *"add +919545296699"* | Adds participant to your last commitment |
| *"what events are happening"* | Lists available events |
| *"show my transaction history"* | Shows recent transactions |

---

## 🏗️ Architecture

```mermaid
graph TB
    A[WhatsApp User] -->|Natural Language| B[Twilio API]
    T[Telegram User] -->|Natural Language| U[Telegram Bot API]
    B --> C[FastAPI Backend]
    U --> C
    C --> D[NL Mapper + Command Parser]
    D --> E[Conversation State Manager]
    E --> F[Service Layer]
    F --> G[(PostgreSQL / Neon)]
    F --> H[Algorand SDK]
    H --> I[Algorand TestNet]
    F --> J[Smart Contracts - PyTeal]
    J --> I
    F --> K[Notification Service]
    K --> B
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Chat Interface** | WhatsApp (Twilio) + Telegram | Multi-platform messaging |
| **Backend** | FastAPI + Uvicorn (Python 3.11) | Async API server |
| **Database** | PostgreSQL / Neon Serverless | User data & transactions |
| **Blockchain** | Algorand TestNet | Decentralized ledger |
| **Smart Contracts** | PyTeal → TEAL → AVM | Bill split, fundraising, escrow, NFT tickets |
| **NLP** | Custom NL Mapper + Command Parser | Natural language understanding |
| **State Machine** | In-memory conversation manager | Multi-step guided flows |
| **Security** | AES-256 (Fernet), rate limiting | Key encryption & API protection |
| **Notifications** | Twilio API | Proactive WhatsApp messages |
| **Tunneling** | ngrok | Development webhook forwarding |

---

## 📁 Project Structure

```
AlgoChat_Pay/
├── backend/                         # Core API Server
│   ├── main.py                     # FastAPI app, routers, middleware
│   ├── config.py                   # Environment config (pydantic-settings)
│   ├── database.py                 # SQLAlchemy engine & sessions
│   ├── algorand/
│   │   └── client.py              # Algorand SDK wrapper
│   ├── models/
│   │   ├── transaction.py         # Transaction records
│   │   ├── commitment.py          # PaymentCommitment, Participant, Reliability
│   │   ├── event.py               # Events for ticketing
│   │   ├── ticket.py              # NFT tickets
│   │   ├── split.py               # Bill splits
│   │   └── merchant.py            # Merchant payments
│   ├── services/
│   │   ├── wallet_service.py      # Wallet creation & encryption
│   │   ├── payment_service.py     # ALGO transfers
│   │   ├── split_service.py       # Bill splitting logic
│   │   ├── ticket_service.py      # NFT ticket minting & verification
│   │   ├── fund_service.py        # Fundraising campaigns
│   │   ├── commitment_service.py  # Escrow lock/release/cancel
│   │   ├── escrow_service.py      # Algorand escrow contracts
│   │   ├── notification_service.py# WhatsApp notifications via Twilio
│   │   └── nl_mapper.py           # Natural language → command mapper
│   ├── routes/                     # API endpoints (health, admin, metrics)
│   ├── middleware/                 # Logging & security middleware
│   └── security/                   # Rate limiting, auth utilities
│
├── bot/                             # Chat Bot Handlers
│   ├── whatsapp_webhook.py        # Twilio WhatsApp webhook (950+ lines)
│   ├── telegram_webhook.py        # Telegram Bot API webhook
│   ├── command_parser.py          # Regex command parser (27 command types)
│   ├── conversation_state.py      # Multi-step conversation state machine
│   ├── commitment_commands.py     # Commitment/escrow command handlers
│   ├── response_templates.py      # 20+ formatted response templates
│   └── button_menus.py            # Interactive button layouts
│
├── projects/
│   ├── contracts/                  # PyTeal smart contracts (3 production)
│   └── frontend/                   # React dashboard
│
├── scripts/                        # Seeding, demo, simulation tools
├── tests/                          # pytest integration tests
├── .env.example                    # Environment variable template
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container deployment
└── docker-compose.yml              # One-command deployment
```

---

## 🔧 Smart Contracts

### Built with PyTeal

**Location:** [`projects/contracts/`](projects/contracts/)

| Contract | Purpose | Key Features |
|----------|---------|--------------|
| **split_payment.py** | Bill Splitting | Atomic transfers, automatic fair division |
| **fundraising_pool.py** | Crowdfunding | Auto-refund if goal not met, transparent tracking |
| **ticket_nft.py** | Event Ticketing | Unique ASAs, anti-scalping, resale royalties |

---

## ⚙️ Setup Guide

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or [Neon Postgres](https://neon.tech) serverless)
- Twilio account (WhatsApp sandbox)
- ngrok account (for development)

### Step 1: Clone & Install

```bash
git clone https://github.com/AnshGoyanka/Algochat_Pay.git
cd Algochat_Pay

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
```

```env
DATABASE_URL=postgresql://user:pass@host/db
ALGORAND_NETWORK=testnet
ENCRYPTION_KEY=your-32-byte-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### Step 3: Start Server

```bash
uvicorn backend.main:app --reload --port 8000
```

### Step 4: Setup Webhook (Development)

```bash
# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL and configure in:
# Twilio Console → WhatsApp Sandbox → Webhook URL
# https://your-ngrok-url.ngrok-free.dev/webhook/whatsapp
```

### Step 5: Test

Send **"hi"** or **"balance"** to your Twilio WhatsApp sandbox number.

### Docker Deployment

```bash
docker-compose up -d
```

---

## 🔐 Security

| Feature | Implementation |
|---------|----------------|
| **Private Key Storage** | AES-256 encryption (Fernet) |
| **Database Security** | SQLAlchemy ORM (SQL injection prevention) |
| **API Security** | Rate limiting + input validation |
| **Webhooks** | HTTPS only (via ngrok / production TLS) |
| **Audit Trail** | All transactions logged on-chain |
| **Secrets Management** | `.env` file (git-ignored) |

---

## 🎯 Why AlgoChat Pay Wins

| | Traditional Solutions | AlgoChat Pay |
|---|---|---|
| **User Acquisition** | Download app, create account | Already on WhatsApp |
| **Learning Curve** | Seed phrases, gas fees | Just text naturally |
| **Network Effect** | Start from zero | 2B WhatsApp users |
| **Transaction Speed** | Minutes to days | 4.5 seconds |
| **Transaction Cost** | $5–50 (Ethereum) | $0.001 (Algorand) |
| **Campus Adoption** | Weeks of onboarding | 77% same-day activation |
| **Multi-Platform** | Single app only | WhatsApp + Telegram |

---

## 📈 Roadmap

### Phase 1: Campus Launch ✅
- [x] WhatsApp + Telegram bot with 7 core feature modules
- [x] 3 production smart contracts (PyTeal)
- [x] Conversational UI with natural language
- [x] Payment commitments with escrow
- [x] Proactive notifications
- [x] Reliability scoring system
- [x] 500+ active beta users

### Phase 2: Feature Expansion (Q3 2026)
- [ ] Non-custodial wallet option (WalletConnect)
- [ ] USDC/USDT stablecoin support
- [ ] Multi-language support (Hindi, Tamil, Spanish)
- [ ] Group chat bill splitting

### Phase 3: Merchant Integration (Q4 2026)
- [ ] Campus store payment terminals
- [ ] QR code payments
- [ ] Recurring subscriptions (meal plans, gym)

### Phase 4: Scale (2027)
- [ ] 50+ university rollout
- [ ] DeFi integrations (yield, lending)
- [ ] Developer API for third-party apps

---

## 👥 Team

**Team Xion**
Ansh Goyanka — Founder & Lead Developer

Built for **Algorand Hackathon 2026**

---

## 🌟 The Vision

**Today:** 500 students on 1 campus use AlgoChat Pay instead of Venmo.

**Tomorrow:** 50M students across 10,000 campuses transact on Algorand without knowing it.

> *"The best technology is invisible. Students don't care about Algorand's 4.5s finality or carbon-negative consensus. They care that splitting a dinner takes 5 seconds, not 5 days."*

---

<div align="center">

**Built with ❤️ by students, for students**

[⭐ Star this repo](https://github.com/AnshGoyanka/Algochat_Pay) · [🐛 Report Bug](https://github.com/AnshGoyanka/Algochat_Pay/issues) · [💡 Request Feature](https://github.com/AnshGoyanka/Algochat_Pay/issues)

</div>

