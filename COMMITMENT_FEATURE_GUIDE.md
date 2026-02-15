# 🔒 Payment Lock Commitments - Feature Guide

## Problem Solved

**"I'll pay you later" never happens.**

In campus life, trip payments and event costs never settle on time. Organizers chase people manually. No system forces commitment.

## Solution: Blockchain Escrow with Social Accountability

Lock funds in advance → Auto-release on deadline → Social pressure for non-payers

---

## How It Works

### For Organizers

1. **Create a Commitment**
   ```
   /lock create Goa Trip 500 5 7
   ```
   - Title: "Goa Trip"
   - Amount: 500 ALGO per person
   - Participants: 5 people
   - Deadline: 7 days from now

2. **Share with Group**
   - Participants lock funds: `/commit 123`
   - Or add them manually: `/add 123 +919999999999`

3. **Auto-Release on Deadline**
   - Funds automatically release to you
   - No manual collection needed
   - Everyone who locked gets marked as reliable

4. **Cancel if Needed**
   - Cancel anytime: `/cancel 123`
   - All participants get automatic refunds

### For Participants

1. **Get Invited**
   - Organizer adds you or shares commitment ID

2. **Lock Your Funds**
   ```
   /commit 123
   ```
   - Funds move to escrow (blockchain-held)
   - You can't access them until deadline
   - Automatic refund if trip canceled

3. **Track Status**
   ```
   /commitment 123
   ```
   - See who's paid
   - See who's pending
   - Days until deadline

4. **Build Reliability Score**
   - Lock on time → Score increases
   - Miss deadline → Score decreases
   - Everyone can see your score

---

## Commands Reference

### Creating Commitments

**Create a new commitment:**
```
/lock create [title] [amount] [participants] [days]
```

Examples:
- `/lock create Goa Trip 500 5 7` - 500 ALGO, 5 people, 7 days
- `/lock create Concert 50 10 3` - 50 ALGO, 10 people, 3 days
- `/lock create Manali Trip 800 8 14` - 800 ALGO, 8 people, 14 days

### Participating

**Lock your funds:**
```
/commit [commitment_id]
```

Examples:
- `/commit 123` - Lock funds for commitment #123

**View status:**
```
/commitment [commitment_id]
```

Examples:
- `/commitment 123` - See who's paid, who hasn't

### Managing

**Add participants:**
```
/add [commitment_id] [phone]
```

Examples:
- `/add 123 +919999999999` - Add participant to commitment #123

**Cancel and refund:**
```
/cancel [commitment_id]
```

Examples:
- `/cancel 123` - Cancel commitment #123 and refund all

### Social Features

**Check your reliability:**
```
/reliability
```

Shows:
- Your reliability score (0-100)
- Badge (💎 Diamond, 🏆 Trophy, ⭐ Star, etc.)
- Fulfilled vs missed commitments
- Recent commitment history

**View your commitments:**
```
/my commitments
```

Shows:
- All commitments you're part of
- Locked vs pending status
- Quick actions

---

## Technical Flow

### 1. Creation
```
Organizer → Create Commitment → Escrow Account Generated
                                          ↓
                              Unique blockchain address
```

### 2. Locking
```
Participant → Lock Funds → Escrow (Smart Contract)
                                 ↓
                     Funds held on blockchain
                     Cannot be accessed by anyone
```

### 3. Release (Deadline Passed)
```
Deadline → Auto-Release → Funds to Organizer
             ↓
  Participants marked as RELEASED (reliable)
  Non-payers marked as MISSED (unreliable)
```

### 4. Cancel (Organizer Triggered)
```
Organizer → Cancel → Refund All Participants
                            ↓
                All funds returned automatically
```

---

## Social Accountability System

### Reliability Score

**How it works:**
- Start at 100/100
- Lock on time: +5 points
- Miss deadline: -10 points
- Score visible to everyone

**Badges:**
- 💎 95+ - Diamond (Highly Reliable)
- 🏆 85-94 - Trophy (Very Reliable)
- ⭐ 70-84 - Star (Reliable)
- 🔵 50-69 - Blue (Average)
- ⚠️ <50 - Warning (Unreliable)

**Why it matters:**
- Organizers see scores before adding people
- Social pressure to pay on time
- Build reputation for reliability

### Leaderboard (Coming Soon)

Rankings by:
- Highest reliability scores
- Most commitments fulfilled
- Fastest to lock funds

---

## Real-World Examples

### Example 1: College Trip

**Setup:**
```
Ansh: /lock create Manali Trip 800 8 10
Bot: ✅ Created #456 - 800 ALGO per person, 10 days deadline
```

**Participants Lock:**
```
Priya: /commit 456
Bot: 🔒 Locked 800 ALGO ✓

Rahul: /commit 456
Bot: 🔒 Locked 800 ALGO ✓

...
```

**Status Check:**
```
Anyone: /commitment 456
Bot: 
📊 Manali Trip Status
✅ Locked: 6/8 participants
⏳ Pending: Rohit, Sanya
💰 Total: 4,800 / 6,400 ALGO
📅 3 days left
```

**Auto-Release:**
```
Day 10:
Bot → Ansh: ✅ 4,800 ALGO released!
Bot → Rohit: ⚠️ You missed the deadline - marked unreliable
```

### Example 2: Event Tickets

**Setup:**
```
Event Organizer: /lock create Concert Tickets 50 20 2
Bot: ✅ Created #789 - 50 ALGO per person, 2 days deadline
```

**Quick Locks:**
```
20 people: /commit 789
Bot: 🔒 All tickets locked! 100% participation
```

**Release:**
```
Day 2:
Bot → Organizer: ✅ 1,000 ALGO released for concert tickets!
```

---

## Security Features

### Blockchain Escrow
- Funds held in Algorand smart contract
- No single party can access funds
- Transparent on blockchain explorer

### Automatic Execution
- No manual intervention needed
- Time-locked releases
- Trustless system

### Refund Safety
- Organizer can cancel anytime
- Automatic refunds to all participants
- On-chain proof of refund

---

## Use Cases

### Campus Life
- 🏔️ Trip payments (Goa, Manali, etc.)
- 🎫 Event tickets in bulk
- 🍕 Group food orders
- 📚 Shared textbook purchases
- 🎉 Party cost splits

### Events
- 🏟️ Sports tournament entries
- 🎭 Theater group bookings
- 🎵 Concert group tickets
- 🏨 Hostel room sharing

### General
- 💰 Any advance payment needed
- 📅 Time-bound commitments
- 👥 Group purchases
- 🤝 Trust-building payments

---

## Benefits

### For Organizers
✅ No chasing people for money  
✅ Funds guaranteed before deadline  
✅ Automatic collection  
✅ Cancel and refund easily  
✅ Social pressure on non-payers  

### For Participants
✅ Trust that money is safe  
✅ Automatic refund if canceled  
✅ Build reliability reputation  
✅ No "forgot to pay" excuses  
✅ Transparent tracking  

### For Everyone
✅ Solves "I'll pay later" problem  
✅ Blockchain-secured escrow  
✅ Social accountability  
✅ WhatsApp-native experience  
✅ Zero manual work  

---

## Setup & Installation

### 1. Initialize Database Tables
```bash
python scripts/init_commitments.py
```

This creates:
- `payment_commitments` - Main commitment records
- `commitment_participants` - Participant tracking
- `commitment_reminders` - Auto-reminder system
- `reliability_scores` - Social scoring system

### 2. Test Commands
```
/lock create Test Trip 100 3 1
/commit [id]
/commitment [id]
/reliability
```

### 3. Background Jobs (Optional)
For production, set up cron jobs:
- Auto-release on deadlines
- Reminder notifications
- Reliability score updates

---

## API Reference

### Services

**CommitmentService** (`backend/services/commitment_service.py`)
- `create_commitment()` - Create new commitment
- `lock_funds()` - Lock participant funds
- `release_commitment()` - Release to organizer
- `cancel_commitment()` - Cancel and refund
- `get_commitment_status()` - Get full status

**EscrowService** (`backend/services/escrow_service.py`)
- `create_escrow_account()` - Generate escrow address
- `lock_funds_to_escrow()` - Send funds to escrow
- `release_escrow_to_organizer()` - Release to organizer
- `refund_from_escrow()` - Refund participants

### Models

**PaymentCommitment** - Main commitment record  
**CommitmentParticipant** - Individual participant  
**CommitmentReminder** - Auto-reminder config  
**ReliabilityScore** - User reliability tracking

---

## Troubleshooting

### "Insufficient balance"
- Check balance: `/balance`
- Need amount + 0.001 ALGO for transaction fee

### "Commitment not found"
- Use correct commitment ID
- Check with `/my commitments`

### "Only organizer can cancel"
- Only the person who created can cancel
- Participants cannot cancel

### "Deadline has passed"
- Can't lock after deadline
- Funds already released to organizer

---

## Roadmap

### Phase 1 (Current) ✅
- Basic commitment creation
- Fund locking
- Auto-release
- Reliability scoring

### Phase 2 (Coming Soon)
- Auto-reminders (24h, 48h before deadline)
- WhatsApp notifications for all events
- Leaderboards
- Partial refunds

### Phase 3 (Future)
- Group chat integration
- Photo/video proof for commitments
- Milestone-based partial releases
- Multi-currency support

---

## Support

**Questions?**
- Check `/help`
- View examples above
- Test with small amounts first

**Issues?**
- Check troubleshooting section
- Verify database tables created
- Check Algorand testnet status

---

**Built with:**
- 🔗 Algorand Blockchain (Escrow)
- 💬 WhatsApp Business API
- 🔒 Smart Contracts (Time-locks)
- 📊 PostgreSQL (State tracking)

**Status:** ✅ Production Ready  
**Network:** Algorand TestNet  
**Version:** 1.0.0
