# Conversational Commitment Creation Guide

## Overview

The **Payment Lock Commitment** feature now supports **natural language conversation**! No need to remember complex command syntax - just tell the bot what you want, and it will guide you through the process step by step.

## How It Works

### Old Way (Still Works)
```
/lock create Goa Trip 500 5 7
```
❌ Hard to remember exact syntax  
❌ Easy to make mistakes  
❌ Not user-friendly

### New Way ✨
```
User: make a goa trip
Bot: How much should each person pay?
User: 500
Bot: How many participants total?
User: 5 people
Bot: How many days until deadline?
User: 7
Bot: [Shows summary] Create this commitment?
User: yes
Bot: ✅ Commitment created!
```
✅ Natural conversation  
✅ Bot guides you  
✅ No syntax to memorize

---

## Starting a Conversation

You can start a commitment conversation with any of these phrases:

### Pattern 1: "make a [title] trip"
```
make a goa trip
make a mumbai trip
make kokan trip
```
→ Creates: "Goa Trip", "Mumbai Trip", "Kokan Trip"

### Pattern 2: "create [title]"
```
create birthday party
create hackathon
create a weekend getaway
```
→ Creates: "Birthday Party", "Hackathon", "Weekend Getaway"

### Pattern 3: "new commitment for [title]"
```
new commitment for college fest
new commitment for trip
```
→ Creates: "College Fest", "Trip"

### Pattern 4: "start lock for [title]"
```
start lock for team dinner
start lock for event
```
→ Creates: "Team Dinner", "Event"

---

## Conversation Flow

### Step 1: Trigger
```
You: make a goa trip
```

Bot detects intent and extracts title "Goa Trip"

### Step 2: Amount
```
Bot: 🎯 Creating: Goa Trip
     💰 How much should each person pay?

You: 500
   or: 500 ALGO
   or: 100.5
```

Bot accepts:
- Plain numbers: `500`
- With currency: `500 algo`, `100 ALGO`
- Decimals: `100.5`

### Step 3: Participants
```
Bot: 🎯 Creating: Goa Trip
     💰 Amount: 500 ALGO per person
     👥 How many participants in total?

You: 5
   or: 5 people
   or: 10 participants
```

Bot accepts:
- Plain numbers: `5`
- With words: `5 people`, `10 participants`
- Range: 2-100 participants

### Step 4: Deadline
```
Bot: 🎯 Creating: Goa Trip
     💰 Amount: 500 ALGO per person
     👥 Participants: 5 people
     ⏰ How many days until deadline?

You: 7
   or: 7 days
   or: 14 days
```

Bot accepts:
- Plain numbers: `7`
- With words: `7 days`, `14 days`
- Range: 1-365 days

### Step 5: Confirmation
```
Bot: 📋 Commitment Summary
     
     🎯 Title: Goa Trip
     💰 Per Person: 500 ALGO
     👥 Participants: 5 people
     ⏰ Deadline: 7 days from now
     
     ✅ Create this commitment?

You: yes
   or: y, confirm, ok, sure, yeah
```

Bot accepts confirmation:
- Yes: `yes`, `y`, `confirm`, `ok`, `sure`, `yeah`
- No: `no`, `n`, `cancel`, `nope`

### Step 6: Success!
```
Bot: ✅ Payment Commitment Created!
     
     🏷️ Goa Trip
     💰 500 ALGO per person
     👥 5 participants needed
     📅 Deadline: Feb 22, 2026
     🆔 Commitment ID: #2
     
     📢 Share with participants:
     "Lock your payment: /commit 2"
```

---

## Canceling Anytime

You can cancel the conversation at any step:

```
You: make a goa trip
Bot: How much should each person pay?
You: 500
Bot: How many participants?
You: cancel

Bot: ❌ Cancelled! No commitment created.
```

**Cancel commands:** `cancel`, `stop`, `quit`, `exit`

---

## Validation

The bot validates your inputs:

### Invalid Amount
```
You: abc
Bot: ❌ Please enter a valid amount (e.g., 100 or 500).
```

### Invalid Participants
```
You: 1
Bot: ❌ Please enter a valid number of participants (2-100).
```

### Invalid Deadline
```
You: 0
Bot: ❌ Please enter a valid number of days (1-365).
```

---

## Timeout Protection

If you don't respond for **10 minutes**, the conversation expires:

```
[10 minutes pass]

You: 500
Bot: ⏱️ Conversation timed out. Start over by saying 
     'create [title]' or 'make a [title] trip'.
```

This prevents stale conversations from interfering with new commands.

---

## Examples

### Example 1: College Trip
```
You: make a college trip
Bot: How much should each person pay?
You: 1000 ALGO
Bot: How many participants?
You: 10
Bot: How many days until deadline?
You: 14
Bot: [Summary] Create this commitment?
You: yes
Bot: ✅ Commitment #3 created!
```

### Example 2: Birthday Party
```
You: create birthday party
Bot: How much should each person pay?
You: 200
Bot: How many participants?
You: 8 people
Bot: How many days until deadline?
You: 5 days
Bot: [Summary] Create this commitment?
You: yes
Bot: ✅ Commitment #4 created!
```

### Example 3: Cancelled Mid-Way
```
You: new commitment for hackathon
Bot: How much should each person pay?
You: 500
Bot: How many participants?
You: cancel
Bot: ❌ Cancelled! No commitment created.
```

---

## Tips

1. **Be natural**: No need for perfect syntax. "5 people" and "5" both work.

2. **Review before confirming**: The bot shows a complete summary before creating the commitment.

3. **Cancel anytime**: Just type `cancel` at any step if you change your mind.

4. **Old commands still work**: If you prefer, you can still use `/lock create [title] [amount] [participants] [days]`.

5. **Title extracted automatically**: The bot extracts the title from your trigger phrase. "make a goa trip" → "Goa Trip"

---

## Next Steps

After creating a commitment:

1. **Share the ID** with participants: `/commit [ID]`
2. **Add participants**: `/add [ID] +91XXXXXXXXXX`
3. **Check status**: `/status [ID]`
4. **View your commitments**: `/commitments`

---

## Troubleshooting

### "I didn't understand that"
- You may have sent a command that looks like a number outside of a conversation
- Start a new conversation with a trigger phrase

### "Conversation timed out"
- You took more than 10 minutes to respond
- Start over with a new trigger phrase

### Creation Failed
- Check your balance (need enough ALGO for escrow account creation)
- Ensure amount is positive
- Participants must be 2-100
- Deadline must be 1-365 days

---

## Comparison

| Feature | Old Command | Conversational |
|---------|-------------|----------------|
| **Syntax** | `/lock create Goa Trip 500 5 7` | `make a goa trip` |
| **Memorization** | Required | Not needed |
| **Guidance** | None | Bot asks questions |
| **Validation** | After submission | Step-by-step |
| **Cancellation** | Can't cancel mid-way | Cancel anytime |
| **User-Friendly** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Coming Soon

- 📱 Add participants via conversation
- 🔔 Customize reminder timing
- 📊 View leaderboard via conversation
- 💬 More natural language patterns

---

**Ready to try it?**

Just say: `make a goa trip` and the bot will guide you! 🚀
