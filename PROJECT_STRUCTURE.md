# AlgoChat Pay - Complete Project Structure

## Project Overview

AlgoChat Pay has a **dual structure**:
1. **Hackathon Submission** (`projects/`) - AlgoKit-compliant showcase
2. **Production System** (`backend/`, `bot/`, `scripts/`) - Real WhatsApp bot

```
algochat-pay/
│
├── projects/                          # 🎯 HACKATHON SUBMISSION
│   ├── contracts/                     # Smart Contracts (PyTeal)
│   │   ├── split_payment.py           # Bill splitting logic
│   │   ├── fundraising_pool.py        # Fundraising campaigns
│   │   ├── ticket_nft.py              # Event ticket NFTs
│   │   ├── build.py                   # Contract build automation
│   │   └── README.md
│   │
│   └── frontend/                      # Interactive Dashboard (React)
│       ├── src/
│       │   ├── App.tsx                # Main dashboard component
│       │   ├── main.tsx               # React entry point
│       │   └── index.css              # TailwindCSS styles
│       ├── package.json               # React + Vite + TailwindCSS
│       ├── vite.config.ts             # Vite configuration
│       ├── tailwind.config.js         # Algorand theme colors
│       └── README.md
│
├── backend/                           # 🚀 PRODUCTION SYSTEM (FastAPI)
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration management
│   ├── database.py                    # Database connection & session
│   │
│   ├── models/                        # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py                    # User/Wallet model
│   │   ├── transaction.py             # Transaction records
│   │   ├── fund.py                    # Fundraising pools
│   │   └── ticket.py                  # Event ticket NFTs
│   │
│   ├── services/                      # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── wallet_service.py          # Wallet creation & management
│   │   ├── payment_service.py         # Payment processing
│   │   ├── ticket_service.py          # NFT ticket operations
│   │   ├── fund_service.py            # Fundraising operations
│   │   └── pitch_metrics_service.py   # Demo metrics calculator
│   │
│   ├── algorand/                      # Algorand SDK Wrapper
│   │   ├── __init__.py
│   │   └── client.py                  # Algorand client (wallet, tx, ASA)
│   │
│   ├── security/                      # Security Layer
│   │   ├── __init__.py
│   │   └── encryption.py              # AES-256 encryption for keys
│   │
│   ├── routes/                        # API Endpoints
│   │   ├── __init__.py
│   │   ├── wallet.py                  # Wallet routes
│   │   ├── payment.py                 # Payment routes
│   │   └── demo.py                    # Demo & pitch endpoints
│   │
│   └── utils/                         # Utility Functions
│       ├── __init__.py
│       ├── helpers.py                 # Common helpers
│       ├── logging_config.py          # Logging setup
│       ├── demo_guardian.py           # Demo health checks
│       └── demo_safe_mode.py          # Transaction limits
│
├── bot/                               # WhatsApp Bot Integration
│   ├── __init__.py
│   ├── whatsapp_webhook.py            # Twilio webhook handler
│   ├── command_parser.py              # NLP command parser
│   └── response_templates.py          # Message templates
│
├── scripts/                           # Demo & Operations Tools
│   ├── demo_scenario_runner.py        # Pre-programmed demo flows
│   ├── judge_answer_helper.py         # Q&A for judges (20 answers)
│   ├── final_pitch_export.py          # Pitch deck generator
│   ├── demo_storyline_generator.py    # 5-min/3-min/1-min scripts
│   ├── create_test_wallets.py         # Test wallet creation
│   └── fund_wallets.py                # TestNet funding
│
├── tests/                             # Test Suite
│   └── (unit & integration tests)
│
├── logs/                              # Application Logs
│   └── algochat.log
│
├── .algokit/                          # AlgoKit Cache
├── .algokit.toml                      # AlgoKit workspace config
├── .editorconfig                      # Coding standards
├── .github/                           # GitHub Actions
│   └── workflows/
│       └── build-test.yml             # CI/CD pipeline
│
├── .env.example                       # Environment template
├── .env                               # Environment variables (DO NOT COMMIT)
├── .gitignore                         # Git ignore rules
├── .dockerignore                      # Docker ignore rules
│
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Docker image definition
├── docker-compose.yml                 # Multi-container setup
│
├── start.py                           # Quick start script
├── run.sh                             # Linux/Mac quick start
├── run.bat                            # Windows quick start
│
├── LICENSE                            # MIT License
├── README.md                          # Main documentation
├── PROJECT_STRUCTURE.md               # This file
├── HACKATHON_SUBMISSION.md            # Submission guide
├── PRODUCTION_DEPLOYMENT.md           # Production deployment guide
├── DEMO_CONTROL_README.md             # Demo system guide
├── DEMO_CONTROL_COMPLETE.md           # Complete demo docs
├── DEMO_QUICK_REFERENCE.txt           # Quick cheatsheet
├── DEMO_INTELLIGENCE.md               # Demo intelligence
└── AlgoChat-Pay.code-workspace        # VS Code workspace

```

## Two Modes of Operation

### 1. Hackathon Showcase Mode (For Judges)

**What:** Interactive React dashboard visualizing AlgoChat Pay features

**Run:**
```bash
# Terminal 1: Start backend API
uvicorn backend.main:app --reload

# Terminal 2: Start frontend dashboard
cd projects/frontend
npm install
npm run dev

# Access: http://localhost:3000
```

**Purpose:** Let judges explore the system without needing WhatsApp

### 2. Production Mode (Real WhatsApp Bot)

**What:** Complete production system with 500 active students

**Run:**
```bash
# Option A: Docker Compose
docker-compose up -d

# Option B: Manual
python start.py
```

**Purpose:** Real-world WhatsApp bot handling actual transactions

---

## Key Files Explained

### Core Application Files

**backend/main.py**
- FastAPI application initialization
- Route registration
- CORS middleware
- Startup/shutdown events

**backend/config.py**
- Environment variable loading
- Settings validation
- Configuration access

**backend/database.py**
- PostgreSQL connection
- SQLAlchemy session management
- Database initialization

### Models (Database Schema)

**models/user.py**
- Maps phone numbers to Algorand wallets
- Stores encrypted private keys
- User activity tracking

**models/transaction.py**
- Records all ALGO transfers
- Transaction status tracking
- Links to smart contracts

**models/fund.py**
- Fundraising campaign data
- Contribution tracking
- Goal/deadline management

**models/ticket.py**
- NFT ticket records
- Ownership tracking
- Validation status

### Services (Business Logic)

**services/wallet_service.py**
- Auto wallet creation
- Balance checking
- Private key decryption (for signing)

**services/payment_service.py**
- ALGO transfers
- Transaction recording
- Balance validation

**services/ticket_service.py**
- NFT minting (Algorand ASAs)
- Ticket verification
- Usage tracking

**services/fund_service.py**
- Campaign creation
- Contribution processing
- Goal tracking

### Algorand Integration

**algorand/client.py**
- Algorand SDK wrapper
- Wallet operations
- Transaction signing
- ASA (NFT) creation

### Security

**security/encryption.py**
- AES-256 Fernet encryption
- Private key encryption/decryption
- Input validation
- Phone number parsing

### WhatsApp Bot

**bot/whatsapp_webhook.py**
- Twilio webhook endpoint
- Message routing
- Response sending

**bot/command_parser.py**
- Natural language parsing
- Command extraction
- Parameter validation

**bot/response_templates.py**
- Pre-formatted messages
- WhatsApp markdown formatting
- User-friendly responses

### Smart Contracts (PyTeal)

**smart_contracts/split_payment_contract.py**
- Group payment settlement
- Equal distribution logic
- Payment tracking

**smart_contracts/fundraising_pool_contract.py**
- Goal-based campaigns
- Automatic refunds
- Deadline enforcement

**smart_contracts/ticket_nft_contract.py**
- Unique ticket verification
- Anti-counterfeiting
- Usage validation

**smart_contracts/deploy.py**
- Compile PyTeal → TEAL
- Deploy to Algorand TestNet
- Save contract IDs

### Scripts

**scripts/create_test_wallets.py**
- Generate test user wallets
- Save to database
- Export details (for funding)

**scripts/fund_wallets.py**
- Bulk fund test wallets
- Transfer from funder account
- Demo preparation

**scripts/test_wallet_service.py**
- Unit tests for wallet creation
- Balance checking tests
- Integration tests

### Docker

**Dockerfile**
- Python 3.11 slim image
- FastAPI application container
- Production-ready setup

**docker-compose.yml**
- PostgreSQL service
- Redis cache
- Backend service
- Network configuration

### Configuration

**.env.example**
- Template for environment variables
- All required keys
- Security notes

**requirements.txt**
- FastAPI ecosystem
- Algorand SDK
- Twilio SDK
- PostgreSQL drivers
- Security libraries
- Testing tools

### Documentation

**README.md**
- Complete setup guide
- Usage examples
- Architecture diagram
- Demo script
- API documentation

**LICENSE**
- MIT License
- Open source friendly

## File Count Summary

- **Python Files**: 35+
- **Smart Contracts**: 3
- **Config Files**: 6
- **Scripts**: 4
- **Documentation**: 3
- **Total Lines of Code**: ~5,000+

## Technology Breakdown

### Backend (70%)
- FastAPI routes and middleware
- SQLAlchemy models
- Service layer business logic
- Algorand SDK integration
- Security & encryption

### Smart Contracts (15%)
- PyTeal contract logic
- Algorand application calls
- State management

### Bot Integration (10%)
- Twilio webhook handling
- Command parsing
- Response generation

### DevOps & Scripts (5%)
- Docker configuration
- Testing utilities
- Deployment scripts

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Quick Start**
   ```bash
   python start.py
   ```

4. **Or Use Docker**
   ```bash
   docker-compose up -d
   ```

---

**Built for Hackspiration - Track 1: Future of Finance**  
**Team Xion | Powered by Algorand**
