# AlgoChat Pay - Smart Contracts

Algorand smart contracts for campus payments, bill splitting, NFT tickets, and fundraising.

## Contracts

### 1. Split Payment Contract
- **File:** `split_payment.py`
- **Purpose:** Atomic bill splitting with automatic distribution
- **Features:** Fair split calculation, automatic settlement, contribution tracking

### 2. Fundraising Pool Contract
- **File:** `fundraising_pool.py`
- **Purpose:** Transparent fundraising campaigns
- **Features:** Goal tracking, contributor list, milestone verification

### 3. Ticket NFT Contract
- **File:** `ticket_nft.py`
- **Purpose:** Event tickets as NFTs
- **Features:** Anti-scalping, verification, resale control

## Development

This project uses PyTeal for smart contract development.

### Build Contracts

```bash
python -m pip install pyteal
python build.py
```

### Deploy Contracts

```bash
python deploy.py --network testnet
```

## Testing

```bash
pytest tests/
```
