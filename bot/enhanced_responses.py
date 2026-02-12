"""
Enhanced response templates
Production-quality error messages and status updates
"""
from typing import Optional


class EnhancedResponseTemplates:
    """
    Enhanced response templates for production demo
    Clear, helpful error messages with retry suggestions
    """
    
    @staticmethod
    def payment_processing(receiver_phone: str, amount: float) -> str:
        """Transaction is being processed"""
        return f"""
⏳ *Processing Payment...*

Sending *{amount} ALGO* to {receiver_phone}

Please wait ~5 seconds for blockchain confirmation...
        """.strip()
    
    @staticmethod
    def payment_retry(attempt: int, max_attempts: int) -> str:
        """Payment retry in progress"""
        return f"""
🔄 *Retrying Payment...*

Attempt {attempt}/{max_attempts}

Network congestion detected. Retrying with backup node...
        """.strip()
    
    @staticmethod
    def payment_failed_insufficient_balance(
        balance: float,
        required: float
    ) -> str:
        """Insufficient balance error"""
        return f"""
❌ *Insufficient Balance*

Your balance: *{balance:.4f} ALGO*
Required: *{required:.4f} ALGO*

💡 *Solutions:*
• Request ALGO from the faucet: https://bank.testnet.algorand.network/
• Ask a friend to send you ALGO
• Reduce the payment amount

Type `balance` to check your wallet.
        """.strip()
    
    @staticmethod
    def payment_failed_network_error(retry_suggested: bool = True) -> str:
        """Network connectivity error"""
        message = """
⚠️ *Network Error*

Could not connect to Algorand network.

This is likely temporary. The system will automatically retry this transaction.
        """.strip()
        
        if retry_suggested:
            message += "\n\n💡 You can also try again in a few seconds."
        
        return message
    
    @staticmethod
    def payment_failed_invalid_address(address: str) -> str:
        """Invalid recipient address"""
        return f"""
❌ *Invalid Address*

The address `{address[:20]}...` is not valid.

💡 *Tips:*
• Algorand addresses are 58 characters
• Must start with a capital letter
• Check for typos

Type `help` for command examples.
        """.strip()
    
    @staticmethod
    def payment_queued_for_retry(queue_position: Optional[int] = None) -> str:
        """Transaction queued for retry"""
        pos_msg = f"\nQueue position: #{queue_position}" if queue_position else ""
        
        return f"""
📋 *Transaction Queued*

Your payment is in queue for retry due to network issues.{pos_msg}

You'll be notified when it completes.

⏱️ Estimated time: 1-2 minutes
        """.strip()
    
    @staticmethod
    def rate_limit_exceeded(retry_after_seconds: int = 60) -> str:
        """Rate limit exceeded"""
        return f"""
⏱️ *Too Many Requests*

You've reached the rate limit for transactions.

Please wait *{retry_after_seconds} seconds* before trying again.

💡 This protects your account from unauthorized access.
        """.strip()
    
    @staticmethod
    def transaction_limit_exceeded(limit: float, limit_type: str = "single") -> str:
        """Transaction limit exceeded"""
        limit_description = {
            "single": "per transaction",
            "daily": "per day"
        }.get(limit_type, "")
        
        return f"""
🚫 *Transaction Limit Exceeded*

Maximum {limit_description}: *{limit} ALGO*

💡 For security, transactions are limited.

Contact support if you need higher limits.
        """.strip()
    
    @staticmethod
    def wallet_created_with_funding_instructions(wallet_address: str) -> str:
        """New wallet with funding instructions"""
        return f"""
🎉 *Wallet Created!*

Your Algorand wallet is ready.

🔑 *Address:*
`{wallet_address}`

⚠️ *Your wallet is empty!*

📥 *Get ALGO (TestNet):*
1. Visit: https://bank.testnet.algorand.network/
2. Paste your address
3. Click "Dispense"
4. Wait ~5 seconds

Then type `balance` to verify!
        """.strip()
    
    @staticmethod
    def command_not_recognized(user_input: str) -> str:
        """Command not recognized"""
        return f"""
❓ *Command Not Recognized*

I didn't understand: "{user_input[:50]}"

Type `help` to see available commands.

*Common commands:*
• `balance` - Check your balance
• `send +1234567890 5` - Send ALGO
• `history` - View transactions
        """.strip()
    
    @staticmethod
    def security_alert_injection_detected() -> str:
        """Security alert for injection attempt"""
        return f"""
🔒 *Security Alert*

Your message contained suspicious characters and was blocked.

For your security, we don't allow special characters in commands.

Type `help` for valid command formats.
        """.strip()
    
    @staticmethod
    def system_maintenance() -> str:
        """System maintenance message"""
        return f"""
🔧 *Maintenance Mode*

AlgoChat Pay is temporarily unavailable for maintenance.

Expected uptime: ~5 minutes

Please try again shortly. Your funds are safe!
        """.strip()
    
    @staticmethod
    def transaction_status_update(
        tx_id: str,
        status: str,
        details: Optional[str] = None
    ) -> str:
        """Generic transaction status update"""
        status_emoji = {
            "pending": "⏳",
            "confirmed": "✅",
            "failed": "❌",
            "retrying": "🔄"
        }.get(status, "ℹ️")
        
        status_text = status.upper()
        details_text = f"\n\n{details}" if details else ""
        
        return f"""
{status_emoji} *Transaction Status: {status_text}*

🔗 TX: `{tx_id[:20]}...`{details_text}
        """.strip()
    
    @staticmethod
    def help_with_examples() -> str:
        """Comprehensive help with examples"""
        return """
📚 *AlgoChat Pay Commands*

💰 *WALLET*
• `balance` - Check your balance
• `address` - Get your wallet address
• `history` - View transaction history

💸 *PAYMENTS*
• `send +1234567890 5` - Send 5 ALGO
• `send +1234567890 2.5 lunch` - Send with note

🍽️ *BILL SPLITTING*
• `split 20 +1111111111 +2222222222 dinner` - Split $20 bill

🎟️ *EVENT TICKETS*
• `ticket buy TechFest 5` - Buy ticket for 5 ALGO
• `ticket validate ABC123` - Validate ticket code

❤️ *FUNDRAISING*
• `fund create 100 Help refugees` - Create fundraiser
• `fund donate FUND123 10` - Donate to campaign

💡 *TIPS*
• Always include country code (+1)
• Amounts are in ALGO
• Messages sent via WhatsApp

Need help? Reply with your question!
        """.strip()
    
    @staticmethod
    def transaction_confirmed_with_explorer_link(
        tx_id: str,
        amount: float,
        network: str = "testnet"
    ) -> str:
        """Transaction confirmed with block explorer link"""
        explorer_base = "https://testnet.algoexplorer.io" if network == "testnet" else "https://algoexplorer.io"
        explorer_url = f"{explorer_base}/tx/{tx_id}"
        
        return f"""
✅ *Transaction Confirmed!*

Amount: *{amount} ALGO*
TX ID: `{tx_id[:16]}...`

🔍 *View on Explorer:*
{explorer_url}

Type `balance` to check your updated balance.
        """.strip()
    
    @staticmethod
    def demo_mode_active() -> str:
        """Demo mode notification"""
        return """
🎬 *DEMO MODE ACTIVE*

This is a demonstration environment running on Algorand TestNet.

✅ All features fully functional
✅ Safe to test transactions
✅ No real money involved

Get started: Type `balance` or `help`
        """.strip()
    
    @staticmethod
    def smart_contract_deployed(
        contract_type: str,
        app_id: int,
        details: str
    ) -> str:
        """Smart contract deployment confirmation"""
        return f"""
🎉 *Smart Contract Deployed!*

Type: *{contract_type}*
App ID: `{app_id}`

{details}

Your contract is live on Algorand!
        """.strip()
    
    @staticmethod
    def error_with_support_info(error_message: str, correlation_id: Optional[str] = None) -> str:
        """Generic error with support information"""
        support_section = ""
        if correlation_id:
            support_section = f"""

🆔 *Error ID:* `{correlation_id}`
(Quote this ID when contacting support)
"""
        
        return f"""
⚠️ *Something Went Wrong*

{error_message}

{support_section}

💡 *What to try:*
• Wait a moment and try again
• Check your balance: `balance`
• View help: `help`

The issue has been logged and we're looking into it.
        """.strip()


# Convenience function for quick access
def get_enhanced_response(response_type: str, **kwargs) -> str:
    """
    Get enhanced response by type
    
    Args:
        response_type: Type of response (e.g., "payment_processing")
        **kwargs: Parameters for the response template
    
    Returns:
        Formatted response message
    """
    template_method = getattr(EnhancedResponseTemplates, response_type, None)
    if template_method:
        return template_method(**kwargs)
    else:
        return f"Response type '{response_type}' not found."
