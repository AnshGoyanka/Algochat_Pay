# AlgoChat Pay - Frontend Dashboard

Interactive dashboard demonstrating AlgoChat Pay features and metrics.

## Features

- **Live Metrics Dashboard** - Real-time campus adoption statistics
- **Demo Showcase** - Interactive demos of payment, bill split, tickets, fundraising
- **Judge Q&A** - Searchable answers to common questions
- **WhatsApp Integration UI** - Visual representation of WhatsApp bot interactions

## Setup

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

## Build

```bash
npm run build
```

## Environment Variables

Create `.env` file:

```bash
# Algorand Network
VITE_ALGOD_SERVER=https://testnet-api.algonode.cloud
VITE_ALGOD_PORT=
VITE_ALGOD_TOKEN=
VITE_ALGOD_NETWORK=testnet

# Indexer
VITE_INDEXER_SERVER=https://testnet-idx.algonode.cloud
VITE_INDEXER_PORT=
VITE_INDEXER_TOKEN=

# Backend API (AlgoChat Pay backend)
VITE_BACKEND_URL=http://localhost:8000
```

## Architecture

This frontend serves as a **showcase dashboard** for hackathon judges. The actual AlgoChat Pay functionality runs through:

- **Backend API** (`../../backend/`) - FastAPI server
- **WhatsApp Bot** (`../../bot/`) - Twilio WhatsApp integration
- **Smart Contracts** (`../contracts/`) - PyTeal contracts on Algorand

This dashboard **visualizes** the system without requiring judges to use WhatsApp.
