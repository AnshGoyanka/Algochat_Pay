"""
Response templates for WhatsApp bot
Human-friendly message formatting with enhanced error handling
"""
from datetime import datetime
from typing import List, Dict, Optional


class ResponseTemplates:
    """
    Pre-formatted response messages
    Uses WhatsApp markdown formatting
    """
    
    @staticmethod
    def welcome_new_user(wallet_address: str, balance: float) -> str:
        return f"""
🎉 *Welcome to AlgoChat Pay!*

Your campus wallet is ready!

💎 *Wallet Address:*
`{wallet_address}`

💰 *Balance:* {balance} ALGO

You can now:
✅ Send & receive ALGO
✅ Split bills with friends
✅ Buy event tickets
✅ Join fundraising campaigns

💡 Tap the buttons below or type:
• `menu` - Quick commands
• `help` - All commands
        """.strip()
    
    @staticmethod
    def balance_info(phone: str, address: str, balance: float) -> str:
        return f"""
💰 *Your Wallet*

📱 Phone: {phone}
🔑 Address: `{address[:10]}...{address[-8:]}`
💎 Balance: *{balance:.4f} ALGO*

💡 Quick actions: `menu` | `history`
        """.strip()
    
    @staticmethod
    def payment_success(
        receiver_phone: str,
        amount: float,
        tx_id: str,
        new_balance: float,
        payment_ref: str = None,
        merchant_name: str = None
    ) -> str:
        explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        
        # Show merchant name if available, otherwise phone
        recipient_display = f"🏪 {merchant_name}" if merchant_name else f"📞 {receiver_phone}"
        payment_id = f"🆔 Payment ID: #{payment_ref}" if payment_ref else f"🔗 TX: `{tx_id[:16]}...`"
        
        return f"""
✅ *Payment Sent!*

💸 Amount: *{amount} ALGO*
{recipient_display}
{payment_id}

💰 New Balance: {new_balance:.4f} ALGO

🔍 *View on Blockchain:*
{explorer_link}

Transaction confirmed in ~4.5 seconds! ⚡
        """.strip()
    
    @staticmethod
    def payment_received(sender_phone: str, amount: float, tx_id: str) -> str:
        explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        return f"""
💰 *Payment Received!*

📥 Amount: *{amount} ALGO*
📞 From: {sender_phone}
🔗 TX: `{tx_id[:16]}...`

🔍 *View on Blockchain:*
{explorer_link}

Type `balance` to check your wallet.
        """.strip()
    
    @staticmethod
    def split_initiated(
        split_bill_id: int,
        amount: float,
        per_person: float,
        participants: List[str],
        description: str
    ) -> str:
        participant_list = "\n".join([f"  • {p}" for p in participants])
        
        return f"""
🍽️ *Bill Split Created!*

🆔 Split ID: {split_bill_id}
💵 Total: {amount} ALGO
👥 Participants: {len(participants) + 1}
💰 Each pays: *{per_person:.2f} ALGO*

📝 *For:* {description}

*Participants:*
{participant_list}

💡 *Everyone can pay their share:*
`pay split {split_bill_id}`

📊 *Check status:*
`view split {split_bill_id}`
        """.strip()
    
    @staticmethod
    def split_payment_success(
        split_bill_id: int,
        amount_paid: float,
        tx_id: str,
        is_fully_paid: bool,
        total_collected: float,
        total_amount: float,
        payment_ref: str = None
    ) -> str:
        status_text = "✅ *SPLIT BILL COMPLETED!*" if is_fully_paid else "✅ *Payment Recorded*"
        explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        payment_id = f"🆔 Payment ID: #{payment_ref}" if payment_ref else f"✅ Transaction: `{tx_id[:12]}...`"
        
        return f"""
{status_text}

🆔 Split ID: {split_bill_id}
💰 You paid: {amount_paid} ALGO
{payment_id}

📊 *Progress:*
💵 Collected: {total_collected:.2f} / {total_amount:.2f} ALGO

🔍 *View on Blockchain:*
{explorer_link}

{"🎉 All participants have paid!" if is_fully_paid else "⏳ Waiting for other participants..."}
        """.strip()
    
    @staticmethod
    def split_details(split_info: Dict) -> str:
        """Format split bill details"""
        payments_text = ""
        for p in split_info["payments"]:
            status = "✅ Paid" if p["is_paid"] else "⏳ Pending"
            payments_text += f"  • {p['phone']}: {p['amount']:.2f} ALGO - {status}\n"
        
        percentage = (split_info['total_collected'] / split_info['total_amount'] * 100) if split_info['total_amount'] > 0 else 0
        
        return f"""
🍽️ *Split Bill Details*

🆔 Split ID: {split_info['id']}
📝 Description: {split_info['description']}
💵 Total: {split_info['total_amount']} ALGO
💰 Per person: {split_info['amount_per_person']:.2f} ALGO

📊 *Payment Status:*
{payments_text}
💵 Collected: {split_info['total_collected']:.2f} / {split_info['total_amount']:.2f} ALGO ({percentage:.0f}%)

{"🎉 Fully paid!" if split_info['is_fully_paid'] else "💡 Pay your share: `pay split " + str(split_info['id']) + "`"}
        """.strip()
    
    @staticmethod
    def my_splits(splits: List) -> str:
        """Format user's pending split bills"""
        if not splits:
            return "📭 No pending split bills.\n\nSplit a bill with: `split 100 ALGO dinner with +91XXX`"
        
        result = "🍽️ *Your Pending Split Bills*\n\n"
        
        for split in splits:
            result += (
                f"[{split.id}] *{split.description}*\n"
                f"     💵 {split.total_amount} ALGO ({split.amount_per_person:.2f} each)\n"
                f"     📊 {split.total_collected:.2f}/{split.total_amount:.2f} collected\n\n"
            )
        
        result += "\n💡 _Pay your share:_ `pay split <ID>`"
        return result.strip()
    
    @staticmethod
    def fund_created(fund_id: int, title: str, goal: float, deadline: datetime) -> str:
        return f"""
🎯 *Fundraising Campaign Created!*

📌 Fund ID: {fund_id}
🎪 Title: *{title}*
💎 Goal: {goal} ALGO
⏰ Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}

Contributors can join with:
`contribute 50 ALGO to fund {fund_id}`

Share fund ID with your network! 🚀
        """.strip()
    
    @staticmethod
    def contribution_success(
        fund_title: str,
        amount: float,
        current: float,
        goal: float,
        tx_id: str,
        payment_ref: str = None,
        beneficiary_name: str = None
    ) -> str:
        percentage = (current / goal * 100) if goal > 0 else 0
        explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        payment_id = f"🆔 Payment ID: #{payment_ref}" if payment_ref else f"🔗 TX: `{tx_id[:16]}...`"
        beneficiary_display = f"\n🏥 Beneficiary: {beneficiary_name}" if beneficiary_name else ""
        
        return f"""
🎉 *Contribution Recorded!*

🎯 Fund: {fund_title}
💰 Your contribution: {amount} ALGO{beneficiary_display}
📊 Progress: {current:.2f} / {goal} ALGO ({percentage:.1f}%)
{payment_id}

🔍 *View on Blockchain:*
{explorer_link}

{"🎊 Goal reached! 🎊" if current >= goal else ""}

Thank you for supporting! 🙏
        """.strip()
    
    @staticmethod
    def fund_details(fund_info: Dict) -> str:
        percentage = fund_info.get("percentage", 0)
        progress_bar = ResponseTemplates._progress_bar(percentage)
        
        contributors_text = ""
        if fund_info.get("contributors"):
            top_3 = fund_info["contributors"][:3]
            contributors_text = "\n\n*Top Contributors:*\n"
            contributors_text += "\n".join([
                f"  • {c['phone']}: {c['amount']} ALGO"
                for c in top_3
            ])
        
        return f"""
🎯 *Fund Details*

📌 ID: {fund_info['id']}
🎪 *{fund_info['title']}*

💰 Raised: {fund_info['current_amount']:.2f} / {fund_info['goal_amount']} ALGO
{progress_bar} {percentage:.1f}%

👥 Contributors: {fund_info['contributions_count']}
📅 Created: {fund_info['created_at'][:10]}
{"✅ Goal Met!" if fund_info['is_goal_met'] else "🔴 Active"}
{contributors_text}

Contribute: `contribute 50 ALGO to fund {fund_info['id']}`
        """.strip()
    
    @staticmethod
    def ticket_purchased(ticket_number: str, event_name: str, ticket_price: float, 
                        venue: str, event_date: str, remaining_tickets: int, tx_id: str,
                       organizer_name: str = None, payment_ref: str = None) -> str:
        from datetime import datetime
        
        # Format event date nicely
        try:
            date_obj = datetime.fromisoformat(event_date)
            date_str = date_obj.strftime("%B %d, %Y at %I:%M %p")
        except:
            date_str = event_date
        
        # Create explorer link
        explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
        organizer_display = f"\n🏢 Organizer: {organizer_name}" if organizer_name else ""
        payment_id = f"\n🆔 Payment ID: #{payment_ref}" if payment_ref else ""
        
        return f"""
🎫 *Ticket Purchased Successfully!*

🎪 *{event_name}*
📍 {venue}
📅 {date_str}
💰 Price: {ticket_price} ALGO{organizer_display}{payment_id}

🔖 *Ticket #:* `{ticket_number}`
✅ This is a unique NFT ticket
🔒 Cannot be duplicated or forged
📲 Stored permanently in your Algorand wallet

🔍 *View NFT on Blockchain:*
{explorer_link}

🎟️ {remaining_tickets} tickets remaining

*Show this ticket number at entry!*
Type `my tickets` to see all your tickets.
        """.strip()
    
    @staticmethod
    def ticket_verification(verification: Dict) -> str:
        if verification["valid"]:
            return f"""
✅ *TICKET VALID*

🔖 Ticket: `{verification['ticket_number']}`
🎪 Event: {verification['event_name']}
👤 Owner: {verification['owner_phone']}
🪙 NFT: {verification['asset_id']}

*Grant entry!*
            """.strip()
        else:
            return f"""
❌ *TICKET INVALID*

🔖 Ticket: `{verification['ticket_number']}`
⚠️ Reason: {verification['reason']}

*Do not grant entry!*
            """.strip()
    
    @staticmethod
    def ticket_list(tickets: List) -> str:
        if not tickets:
            return "📭 You don't have any tickets yet.\n\nType `list events` to see available events!"
        
        ticket_items = []
        for t in tickets:
            status = "✅ Valid" if t.is_valid and not t.is_used else ("⚠️ Used" if t.is_used else "❌ Invalid")
            ticket_items.append(
                f"🎫 *{t.event_name}*\n"
                f"   Ticket: `{t.ticket_number}`\n"
                f"   Status: {status}\n"
                f"   NFT: {t.asset_id}"
            )
        
        return "🎫 *Your Tickets*\n\n" + "\n\n".join(ticket_items)
    
    @staticmethod
    def event_list(events: List) -> str:
        """Format list of available events"""
        if not events:
            return "📭 No events available right now.\n\nCheck back later!"
        
        from datetime import datetime
        
        # Sort events by date first (upcoming events first)
        sorted_events = sorted(events, key=lambda e: e.event_date if e.event_date else datetime.max)
        
        # Group by category
        categories = {}
        for event in sorted_events:
            cat = event.category or "Other"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(event)
        
        # Category emojis
        cat_emojis = {
            "technology": "💻",
            "music": "🎵",
            "sports": "⚽",
            "education": "🎓",
            "culture": "🎭",
            "other": "🎪"
        }
        
        result = "🎫 *Available Events*\n\n"
        display_num = 1
        
        # Define category order
        category_order = ["education", "technology", "music", "sports", "culture", "other"]
        
        for category_key in category_order:
            if category_key not in [c.lower() for c in categories.keys()]:
                continue
                
            # Find the actual category key (might have different casing)
            category = next((c for c in categories.keys() if c.lower() == category_key), None)
            if not category:
                continue
                
            category_events = categories[category]
            emoji = cat_emojis.get(category.lower(), "🎪")
            result += f"{emoji} *{category.upper()}*\n\n"
            
            for event in category_events:
                # Format date
                try:
                    date_obj = datetime.fromisoformat(str(event.event_date))
                    date_str = date_obj.strftime("%b %d")
                except:
                    date_str = "TBA"
                
                # Availability status
                if event.is_sold_out:
                    status = "🔴 SOLD OUT"
                elif event.tickets_available < 50:
                    status = f"🟡 {event.tickets_available} left!"
                else:
                    status = f"🟢 {event.tickets_available} available"
                
                result += (
                    f"[{display_num}] 🎪 *{event.name}*\n"
                    f"     🆔 Event ID: {event.id}\n"
                    f"     📍 {event.venue}\n"
                    f"     📅 {date_str} | 💰 {event.ticket_price} ALGO\n"
                    f"     {status}\n\n"
                )
                display_num += 1
        
        result += "\n💡 _To purchase: use the Event ID:_ `buy ticket 1` or `buy ticket TechFest 2026`"
        return result.strip()
    
    @staticmethod
    def fund_list(funds: List) -> str:
        """Format list of active fundraising campaigns"""
        if not funds:
            return "📭 No active fundraisers right now.\n\nType `create fund Title goal 500 ALGO` to start one!"
        
        from datetime import datetime
        
        result = "🎯 *Active Fundraising Campaigns*\n\n"
        
        for i, fund in enumerate(funds[:5], 1):  # Show top 5
            # Calculate progress
            percentage = (fund.current_amount / fund.goal_amount * 100) if fund.goal_amount > 0 else 0
            
            # Progress bar
            filled = int(percentage / 10)
            bar = "█" * filled + "░" * (10 - filled)
            
            # Goal status
            if fund.is_goal_met:
                status_emoji = "🎉"
                status_text = "GOAL MET!"
            else:
                status_emoji = "🎯"
                status_text = f"{percentage:.0f}%"
            
            # Deadline
            try:
                if fund.deadline:
                    days_left = (fund.deadline - datetime.utcnow()).days
                    if days_left <= 3:
                        deadline_str = f"🚨 {days_left} days left - URGENT!"
                    else:
                        deadline_str = f"⏳ {days_left} days left"
                else:
                    deadline_str = ""
            except:
                deadline_str = ""
            
            # Truncate description to first 100 chars
            desc = fund.description[:100] + "..." if len(fund.description) > 100 else fund.description
            
            result += (
                f"[{i}] {status_emoji} *{fund.title}*\n"
                f"_{desc}_\n"
                f"💰 {fund.current_amount:.1f} / {fund.goal_amount:.1f} ALGO\n"
                f"[{bar}] {status_text}\n"
                f"{deadline_str}\n\n"
            )
        
        result += "\n💡 _To contribute: type_ `contribute 50 ALGO to fund 1`"
        return result.strip()
    
    @staticmethod
    def transaction_history(transactions: List) -> str:
        if not transactions:
            return "📭 No transactions yet.\n\nStart by typing `balance` to check your wallet!"
        
        tx_items = []
        for tx in transactions[:10]:  # Show last 10
            direction = "📤" if tx.sender_phone else "📥"
            amount_str = f"{tx.amount} ALGO"
            timestamp = tx.timestamp.strftime("%m/%d %H:%M") if tx.timestamp else "N/A"
            explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx.tx_id}"
            
            tx_items.append(
                f"{direction} {amount_str} - {tx.transaction_type.value}\n"
                f"   {timestamp} | `{tx.tx_id[:12]}...`\n"
                f"   🔍 {explorer_link}"
            )
        
        return "📊 *Transaction History*\n\n" + "\n\n".join(tx_items)
    
    @staticmethod
    def error_message(error_type: str, details: str = "") -> str:
        messages = {
            "insufficient_balance": "❌ Insufficient balance. Check your wallet with `balance` command.",
            "invalid_phone": "❌ Invalid phone number format. Use: +91XXXXXXXXXX",
            "invalid_amount": "❌ Invalid amount. Must be a positive number.",
            "not_found": f"❌ Not found. {details}",
            "general": f"❌ Error: {details}"
        }
        
        return messages.get(error_type, messages["general"])
    
    @staticmethod
    def unknown_command(text: str) -> str:
        return f"""
🤔 I didn't understand: "{text}"

Type `help` to see available commands!
        """.strip()
    
    @staticmethod
    def quick_menu() -> str:
        """Quick access menu with clickable command shortcuts"""
        return """
⚡ *Quick Commands*

Tap to copy and send:

💰 `balance`
📜 `history`
🎫 `events`
💝 `funds`
💸 `my splits`
🎟️ `my tickets`
❓ `help`

_Reply with any command above!_
        """.strip()
    
    @staticmethod
    def _progress_bar(percentage: float, length: int = 10) -> str:
        """Generate text progress bar"""
        filled = int(percentage / 100 * length)
        empty = length - filled
        return "🟢" * filled + "⚪" * empty
    
    # ===== Conversational Commitment Creation =====
    
    @staticmethod
    def conversation_ask_amount(title: str) -> str:
        """Step 1: Ask for amount per person"""
        return f"""
🎯 *Creating: {title}*

💰 How much should *each person* pay?

_Example: 500 or 100 ALGO_
_Type 'cancel' to stop_
        """.strip()
    
    @staticmethod
    def conversation_ask_participants(title: str, amount: float) -> str:
        """Step 2: Ask for participant count"""
        return f"""
🎯 *Creating: {title}*
💰 Amount: {amount} ALGO per person

👥 How many *participants* in total?

_Example: 5 or 10 people_
_Type 'cancel' to stop_
        """.strip()
    
    @staticmethod
    def conversation_ask_deadline(title: str, amount: float, participants: int) -> str:
        """Step 3: Ask for deadline"""
        return f"""
🎯 *Creating: {title}*
💰 Amount: {amount} ALGO per person
👥 Participants: {participants} people

⏰ How many *days* until deadline?

_Example: 7 or 14 days_
_Type 'cancel' to stop_
        """.strip()
    
    @staticmethod
    def conversation_confirm_commitment(title: str, amount: float, participants: int, days: int) -> str:
        """Step 4: Show summary and ask for confirmation"""
        return f"""
📋 *Commitment Summary*

🎯 *Title:* {title}
💰 *Per Person:* {amount} ALGO
👥 *Participants:* {participants} people
⏰ *Deadline:* {days} days from now

🔒 *Each person* will lock {amount} ALGO in escrow
💸 *Total Pool:* {amount * participants} ALGO
🎁 Organizer gets everyone's locked funds if all commit on time!

✅ *Create this commitment?*
_Reply 'yes' to confirm or 'no' to cancel_
        """.strip()
    
    @staticmethod
    def conversation_cancelled() -> str:
        """User cancelled conversation"""
        return "❌ Cancelled! No commitment created."
    
    @staticmethod
    def conversation_invalid_amount() -> str:
        """Invalid amount entered"""
        return "❌ Please enter a valid amount (e.g., 100 or 500)."
    
    @staticmethod
    def conversation_invalid_participants() -> str:
        """Invalid participant count"""
        return "❌ Please enter a valid number of participants (2-100)."
    
    @staticmethod
    def conversation_invalid_deadline() -> str:
        """Invalid deadline"""
        return "❌ Please enter a valid number of days (1-365)."
    
    @staticmethod
    def conversation_timeout() -> str:
        """Conversation timed out"""
        return "⏱️ Conversation timed out. Start over by saying 'create [title]' or 'make a [title] trip'."


# Global instance
response_templates = ResponseTemplates()
