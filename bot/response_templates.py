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

Type `help` to see all commands!
        """.strip()
    
    @staticmethod
    def balance_info(phone: str, address: str, balance: float) -> str:
        return f"""
💰 *Your Wallet*

📱 Phone: {phone}
🔑 Address: `{address[:10]}...{address[-8:]}`
💎 Balance: *{balance:.4f} ALGO*

Type `history` to see transactions.
        """.strip()
    
    @staticmethod
    def payment_success(
        receiver_phone: str,
        amount: float,
        tx_id: str,
        new_balance: float
    ) -> str:
        return f"""
✅ *Payment Sent!*

💸 Amount: *{amount} ALGO*
📞 To: {receiver_phone}
🔗 TX: `{tx_id[:16]}...`

💰 New Balance: {new_balance:.4f} ALGO

Transaction confirmed in ~4.5 seconds! ⚡
        """.strip()
    
    @staticmethod
    def payment_received(sender_phone: str, amount: float, tx_id: str) -> str:
        return f"""
💰 *Payment Received!*

📥 Amount: *{amount} ALGO*
📞 From: {sender_phone}
🔗 TX: `{tx_id[:16]}...`

Type `balance` to check your wallet.
        """.strip()
    
    @staticmethod
    def split_initiated(
        amount: float,
        per_person: float,
        participants: List[str],
        description: str
    ) -> str:
        participant_list = "\n".join([f"  • {p}" for p in participants])
        
        return f"""
🍽️ *Bill Split Initiated*

💵 Total: {amount} ALGO
👥 Participants: {len(participants) + 1}
💰 Each pays: *{per_person:.2f} ALGO*

📝 *For:* {description}

*Participants:*
{participant_list}

Payment requests sent via WhatsApp!
        """.strip()
    
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
        tx_id: str
    ) -> str:
        percentage = (current / goal * 100) if goal > 0 else 0
        
        return f"""
🎉 *Contribution Recorded!*

🎯 Fund: {fund_title}
💰 Your contribution: {amount} ALGO
📊 Progress: {current:.2f} / {goal} ALGO ({percentage:.1f}%)
🔗 TX: `{tx_id[:16]}...`

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
    def ticket_purchased(event: str, ticket_number: str, asset_id: int) -> str:
        return f"""
🎫 *Ticket Purchased!*

🎪 Event: *{event}*
🔖 Ticket #: `{ticket_number}`
🪙 NFT Asset ID: {asset_id}

✅ This is a unique NFT ticket
🔒 Impossible to duplicate
📲 Stored in your Algorand wallet

Show this ticket number at entry!
Type `my tickets` to see all tickets.
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
            return "📭 You don't have any tickets yet.\n\nType `buy ticket EventName` to purchase!"
        
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
    def transaction_history(transactions: List) -> str:
        if not transactions:
            return "📭 No transactions yet.\n\nStart by typing `balance` to check your wallet!"
        
        tx_items = []
        for tx in transactions[:10]:  # Show last 10
            direction = "📤" if tx.sender_phone else "📥"
            amount_str = f"{tx.amount} ALGO"
            timestamp = tx.timestamp.strftime("%m/%d %H:%M") if tx.timestamp else "N/A"
            
            tx_items.append(
                f"{direction} {amount_str} - {tx.type.value}\n"
                f"   {timestamp} | `{tx.tx_id[:12]}...`"
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
    def _progress_bar(percentage: float, length: int = 10) -> str:
        """Generate text progress bar"""
        filled = int(percentage / 100 * length)
        empty = length - filled
        return "🟢" * filled + "⚪" * empty


# Global instance
response_templates = ResponseTemplates()
