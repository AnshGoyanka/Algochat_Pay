"""
Notification service - Send WhatsApp notifications via Twilio
"""
from twilio.rest import Client
import logging
from backend.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Handles sending WhatsApp notifications to users
    """
    
    def __init__(self):
        """Initialize Twilio client"""
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
    
    def send_whatsapp_notification(self, to_phone: str, message: str) -> bool:
        """
        Send WhatsApp notification to a phone number
        
        Args:
            to_phone: Recipient's phone number (format: +1234567890)
            message: Message text to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith("whatsapp:"):
                to_phone = f"whatsapp:{to_phone}"
            
            # Send message via Twilio
            message = self.client.messages.create(
                from_=self.from_number,
                to=to_phone,
                body=message
            )
            
            logger.info(f"✓ Notification sent to {to_phone}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification to {to_phone}: {e}")
            return False
    
    def notify_payment_received(
        self, 
        receiver_phone: str, 
        sender_phone: str, 
        amount: float,
        payment_ref: str = None,
        tx_id: str = None
    ):
        """
        Notify recipient that they received a payment
        
        Args:
            receiver_phone: Recipient's phone number
            sender_phone: Sender's phone number
            amount: Amount in ALGO
            payment_ref: Payment reference ID
            tx_id: Transaction ID on Algorand blockchain
        """
        # Build message parts
        message_parts = [
            f"💰 *Payment Received!*",
            "",
            f"You received *{amount} ALGO* from {sender_phone}",
            ""
        ]
        
        if payment_ref:
            message_parts.append(f"💳 Payment Ref: {payment_ref}")
        
        if tx_id:
            explorer_link = f"https://testnet.explorer.perawallet.app/tx/{tx_id}"
            message_parts.append(f"🔍 View on Blockchain:")
            message_parts.append(explorer_link)
        
        message_parts.extend([
            "",
            "Check your balance: Type *balance*",
            "View details: Type *history*"
        ])
        
        message = "\n".join(message_parts)
        
        return self.send_whatsapp_notification(receiver_phone, message)
    
    def notify_split_bill_created(
        self,
        participant_phone: str,
        initiator_phone: str,
        split_id: int,
        amount_per_person: float,
        description: str
    ):
        """
        Notify participant that they're included in a split bill
        
        Args:
            participant_phone: Participant's phone number
            initiator_phone: Person who created the split
            split_id: Split bill ID
            amount_per_person: Amount each person owes
            description: Description of the bill
        """
        message = f"""💸 *Bill Split Request*

{initiator_phone} wants to split a bill with you!

📝 {description}
💰 Your share: *{amount_per_person} ALGO*

To pay your share, type:
*pay split {split_id}*

View details: *view split {split_id}*"""
        
        return self.send_whatsapp_notification(participant_phone, message)
    
    def notify_split_payment_received(
        self,
        initiator_phone: str,
        participant_phone: str,
        amount: float,
        split_id: int,
        is_fully_paid: bool
    ):
        """
        Notify initiator that someone paid their share
        
        Args:
            initiator_phone: Person who created the split
            participant_phone: Person who just paid
            amount: Amount paid
            split_id: Split bill ID
            is_fully_paid: Whether all participants have paid
        """
        status = "✅ *All participants have paid!*" if is_fully_paid else "⏳ Waiting for others..."
        
        message = f"""💰 *Split Payment Received*

{participant_phone} paid their share!

💵 Amount: *{amount} ALGO*
Split ID: {split_id}

{status}

View details: *view split {split_id}*"""
        
        return self.send_whatsapp_notification(initiator_phone, message)
    
    def notify_fund_contribution(
        self,
        creator_phone: str,
        contributor_phone: str,
        amount: float,
        fund_title: str,
        total_raised: float,
        goal_amount: float
    ):
        """
        Notify fund creator about a new contribution
        
        Args:
            creator_phone: Fund creator's phone
            contributor_phone: Person who contributed
            amount: Contribution amount
            fund_title: Fund title
            total_raised: Total amount raised so far
            goal_amount: Fundraising goal
        """
        percentage = (total_raised / goal_amount * 100) if goal_amount > 0 else 0
        
        message = f"""❤️ *New Contribution!*

{contributor_phone} contributed *{amount} ALGO*

🎯 {fund_title}
💰 Raised: {total_raised} / {goal_amount} ALGO ({percentage:.1f}%)

Type *view fund* to see details!"""
        
        return self.send_whatsapp_notification(creator_phone, message)


# Global notification service instance
notification_service = NotificationService()
