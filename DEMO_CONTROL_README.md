# Demo Control + Pitch Support System

**Zero-risk demo execution. Data-backed pitch. Instant judge Q&A answers.**

Built for AlgoChat Pay hackathon final round.

---

## 🎯 Quick Start

### Pre-Demo Setup (5 minutes)

```bash
# 1. Check health
python backend/utils/demo_guardian.py

# 2. Enable safe mode
export FINAL_DEMO_MODE=true
uvicorn backend.main:app --reload

# 3. Get pitch metrics
curl http://localhost:8000/demo/pitch-summary

# 4. Review scenarios
python scripts/demo_scenario_runner.py list
```

### Live Demo Execution (4 minutes)

```bash
# Scenario 1: Payment Demo (60 seconds)
python scripts/demo_scenario_runner.py run --scenario 2 --no-pause

# Scenario 2: Bill Split (45 seconds)
python scripts/demo_scenario_runner.py run --scenario 3 --no-pause

# Show Impact Metrics (30 seconds)
curl http://localhost:8000/demo/pitch-summary
```

---

## 📦 What's Included

### 1. Demo Scenario Runner
**File:** `scripts/demo_scenario_runner.py`  
**Purpose:** Predefined demo flows with expected outcomes

5 Complete Scenarios:
- Scenario 1: First user onboarding
- Scenario 2: Peer-to-peer payment ⭐
- Scenario 3: Bill split atomic transfer ⭐
- Scenario 4: NFT ticket purchase
- Scenario 5: Fundraising campaign

```bash
# List all scenarios
python scripts/demo_scenario_runner.py list

# Run specific scenario
python scripts/demo_scenario_runner.py run --scenario 2

# Continuous playback (no pauses)
python scripts/demo_scenario_runner.py all --no-pause
```

### 2. Pitch Metrics Service
**File:** `backend/services/pitch_metrics_service.py`  
**Purpose:** Calculate presentation-ready metrics

5 Core Metrics:
- Adoption rate (activation %, engagement %)
- Daily active wallets
- Transactions per user
- Campus coverage
- Trust savings (fraud prevented, dispute resolution)

```python
from backend.services.pitch_metrics_service import get_pitch_metrics

pitch_service = get_pitch_metrics(db)
adoption = pitch_service.get_adoption_rate()
# {"activation_rate_percent": 77.0, "pitch_statement": "..."}
```

### 3. Judge Q&A Helper
**File:** `scripts/judge_answer_helper.py`  
**Purpose:** Pre-generated answers to 20 common questions

Categories: Security, Regulation, Blockchain Choice, Competition, Economics, Scale, Trust, Operations, Partnerships

```bash
# List all 20 questions
python scripts/judge_answer_helper.py --list

# Get detailed answer
python scripts/judge_answer_helper.py "Why custodial?"

# Get short answer
python scripts/judge_answer_helper.py "Why Algorand?" --short
```

### 4. Demo Health Guardian
**File:** `backend/utils/demo_guardian.py`  
**Purpose:** Pre-demo checklist (10 health checks)

Checks: Database, Users, Transactions, Metrics, Redis, Algorand, Wallets, Scenarios, Environment

```bash
# Run all health checks
python backend/utils/demo_guardian.py

# JSON output
python backend/utils/demo_guardian.py --json

# Exit code: 0 if ready, 1 if not
echo $?
```

### 5. Pitch Summary API
**Endpoint:** `GET /demo/pitch-summary`  
**Purpose:** Instant pitch preparation

Returns:
- Top 5 impact metrics
- Top 3 adoption insights
- Closing statement
- Elevator pitch

```bash
curl http://localhost:8000/demo/pitch-summary
```

### 6. Demo Safe Mode
**File:** `backend/utils/demo_safe_mode.py`  
**Purpose:** Protect production during demo

Features: Transaction limits, wallet whitelisting, metric freezing, blockchain write protection

```bash
# Enable safe mode
export FINAL_DEMO_MODE=true
export DEMO_MAX_TRANSACTION=50.0

# Check status
python backend/utils/demo_safe_mode.py

# Get instructions
python backend/utils/demo_safe_mode.py --enable
```

### 7. Final Pitch Export
**File:** `scripts/final_pitch_export.py`  
**Purpose:** Generate pitch materials

Exports: Slide bullets, speaker notes, one-pagers (judge/investor/press), JSON metrics

```bash
# Export all formats
python scripts/final_pitch_export.py

# Export to custom directory
python scripts/final_pitch_export.py --output-dir pitch_materials

# Export only slides
python scripts/final_pitch_export.py --format slides
```

### 8. Demo Storyline Generator
**File:** `scripts/demo_storyline_generator.py`  
**Purpose:** Generate timed demo scripts

Scripts: 5-minute full demo, 3-minute elevator pitch, 1-minute lightning pitch

```bash
# Export all scripts
python scripts/demo_storyline_generator.py --export

# Preview 5-minute script
python scripts/demo_storyline_generator.py --duration 5

# Preview 1-minute pitch
python scripts/demo_storyline_generator.py --duration 1
```

---

## 🔥 The "Big 5" Metrics

Memorize these numbers:

1. **500** students using platform
2. **77%** activation rate
3. **2,500+** successful transactions
4. **98%** success rate
5. **4.5s** blockchain settlement time

---

## 🎤 Demo Execution Flow

### 4-Minute Live Demo

**[0:00-0:30] Hook**
- "Students splitting $40 lunch bill - how?"
- "AlgoChat Pay. 500 students. 77% activation."

**[0:30-1:30] Payment Demo**
- Run Scenario 2
- "4.5 seconds. Done. 2500+ transactions."

**[1:30-2:15] Bill Split Demo**
- Run Scenario 3
- "Atomic transfer. $0.001 fee vs $5-50 Ethereum."

**[2:15-3:00] Impact Metrics**
- Show `/demo/pitch-summary`
- "77% activation proves product-market fit."

**[3:00-4:00] Closing**
- "500 students. Proven. Scaling to 100 campuses."
- "Questions?"

---

## 🛡️ Pre-Demo Checklist

30 minutes before demo:

- [ ] Run health guardian → All PASS?
- [ ] Enable demo safe mode
- [ ] Start backend server
- [ ] Test scenario runner
- [ ] Verify pitch metrics API
- [ ] Review top 5 Q&A questions
- [ ] Print quick reference card

---

## 🚨 Troubleshooting

**Health check fails?**
```bash
python backend/utils/demo_guardian.py --json
# Fix specific issue, re-run
```

**Transaction fails during demo?**
1. Stay calm
2. Show expected response from scenario file
3. Pivot: "This is why we built monitoring"

**Unknown judge question?**
1. Relate to closest known question
2. Use framework: Problem → Solution → Data → Impact
3. Reference real metrics

---

## 📊 API Endpoints

All demo-related endpoints:

```bash
# Pitch summary (top metrics + insights)
GET /demo/pitch-summary

# Live stats dashboard
GET /demo/live-stats

# Comprehensive metrics
GET /demo/comprehensive

# Success rate breakdown
GET /demo/success-rate

# Transaction types
GET /demo/tx-types
```

---

## 💡 Pro Tips

1. **Practice timing:** Run through 5-minute script at least once
2. **Memorize comeback lines:** "500 students using custodial > 5 experts using self-custody"
3. **Have backup plan:** If live demo fails, show API responses
4. **Use data defensively:** Every claim backed by metric
5. **Keep it simple:** Don't dive into PyTeal unless asked

---

## 📁 File Structure

```
AlgoChat_Pay/
├── scripts/
│   ├── demo_scenario_runner.py      ⭐ 5 demo scenarios
│   ├── judge_answer_helper.py       ⭐ 20 Q&A answers
│   ├── final_pitch_export.py        📄 Pitch materials
│   └── demo_storyline_generator.py  🎤 Demo scripts
├── backend/
│   ├── services/
│   │   └── pitch_metrics_service.py 📊 Metrics calculator
│   ├── utils/
│   │   ├── demo_guardian.py         ✅ Health checks
│   │   └── demo_safe_mode.py        🛡️ Safe mode
│   └── routes/
│       └── demo.py                  🌐 API endpoints
└── docs/
    ├── DEMO_CONTROL_COMPLETE.md     📖 Full guide
    └── DEMO_QUICK_REFERENCE.txt     🎯 Quick reference
```

---

## 🏆 Success Checklist

You're ready when:

- [ ] Health guardian shows all PASS
- [ ] Demo safe mode enabled
- [ ] Can recite "Big 5" metrics from memory
- [ ] Practiced 5-minute demo script
- [ ] Reviewed top 10 Q&A questions
- [ ] Pitch materials exported
- [ ] Scenario runner tested

---

## 📞 Quick Reference

**Emergency Commands:**
```bash
# Health check
python backend/utils/demo_guardian.py

# Safe mode status
python backend/utils/demo_safe_mode.py

# List scenarios
python scripts/demo_scenario_runner.py list

# Get Q&A answer
python scripts/judge_answer_helper.py "Why custodial?"

# Pitch metrics
curl http://localhost:8000/demo/pitch-summary
```

**Elevator Pitch (30 seconds):**
> "AlgoChat Pay is the WhatsApp blockchain wallet for students.
> 500 students, 77% activation, 2500+ transactions.
> Pay via text in 4.5 seconds on Algorand.
> Proven on 1 campus, scaling to 100.
> The future of student payments."

---

## 🚀 Go Time

You have:
- ✅ Zero-risk demo execution
- ✅ Data-backed pitch
- ✅ Instant Q&A answers
- ✅ Professional materials
- ✅ Health monitoring
- ✅ Safe mode protection

**No surprises. No uncertainties. Just confident, impressive demo execution.**

**Go win that hackathon! 🏆**

---

**Generated:** 2025-01-15  
**Version:** Demo Control + Pitch Support v1.0  
**Status:** All 8 tasks complete ✅
