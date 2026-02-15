"""
Commitment Bot Commands - Handle payment lock commitments
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.services.commitment_service import commitment_service
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class CommitmentCommands:
    """
    Bot command handlers for payment commitments
    """
    
    def handle_create_commitment(
        self,
        db: Session,
        organizer_phone: str,
        title: str,
        amount: float,
        participants: int,
        days: int,
        return_id: bool = False
    ):
        """
        Create a new payment commitment
        
        Example: /lock create Goa Trip 500 5 7
        
        Args:
            return_id: If True, return tuple (response, commitment_id). If False, return just response.
        """
        try:
            # Calculate deadline
            deadline = datetime.utcnow() + timedelta(days=days)
            
            # Create commitment
            commitment = commitment_service.create_commitment(
                db=db,
                organizer_phone=organizer_phone,
                title=title,
                amount_per_person=amount,
                total_participants=participants,
                deadline=deadline
            )
            
            # Format response
            response = f"""✅ *Payment Commitment Created!*

🏷️ {commitment.title}
💰 {commitment.amount_per_person} ALGO per person
👥 {commitment.total_participants} participants needed
📅 Deadline: {commitment.deadline.strftime('%b %d, %Y')}
⏰ {commitment.days_until_deadline} days to lock funds

🆔 Commitment ID: *#{commitment.id}*

📢 *Share with participants:*
"Lock your payment: /commit {commitment.id}"

💡 *Add participants:*
Just say "add +91XXXXXXXXXX"
Example: add +918237987667"""
            
            if return_id:
                return (response, commitment.id)
            return response
            
        except Exception as e:
            logger.error(f"Failed to create commitment: {e}")
            error_msg = f"❌ Failed to create commitment: {str(e)}"
            if return_id:
                return (error_msg, None)
            return error_msg
    
    def handle_commit_funds(
        self,
        db: Session,
        participant_phone: str,
        commitment_id: int
    ) -> str:
        """
        Lock participant's funds to commitment
        
        Example: /commit 123
        """
        try:
            # Get commitment details first
            status = commitment_service.get_commitment_status(db, commitment_id)
            
            if not status:
                return f"❌ Commitment #{commitment_id} not found"
            
            # Lock funds
            participant = commitment_service.lock_funds(
                db=db,
                commitment_id=commitment_id,
                participant_phone=participant_phone
            )
            
            # Get updated status
            updated_status = commitment_service.get_commitment_status(db, commitment_id)
            
            response = f"""🔒 *Funds Locked Successfully!*

✅ Locked {participant.amount} ALGO for:
📋 {status['title']}

💳 Transaction: {participant.lock_tx_id[:8]}...
🔗 View: https://testnet.explorer.perawallet.app/tx/{participant.lock_tx_id}

📊 *Commitment Status:*
✅ Locked: {updated_status['participants_locked']}/{updated_status['total_participants']} participants
💰 Total: {updated_status['total_locked']} ALGO

Your funds will be:
• Released to organizer on {status['deadline'].strftime('%b %d')}
• Refunded if commitment canceled

Check status: /commitment {commitment_id}"""
            
            # Notify organizer
            try:
                notification_service.send_whatsapp_notification(
                    to_phone=status['organizer'],
                    message=f"""💰 *New Commitment Lock!*

{participant_phone} locked {participant.amount} ALGO

📋 {status['title']}
📊 Progress: {updated_status['participants_locked']}/{updated_status['total_participants']}

View status: /commitment {commitment_id}"""
                )
            except Exception as e:
                logger.warning(f"Failed to notify organizer: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to lock funds: {e}")
            return f"❌ Failed to lock funds: {str(e)}"
    
    def handle_commitment_status(
        self,
        db: Session,
        commitment_id: int
    ) -> str:
        """
        Show commitment status
        
        Example: /commitment 123
        """
        try:
            status = commitment_service.get_commitment_status(db, commitment_id)
            
            # Status icon
            status_icon = {
                "active": "🟢",
                "completed": "✅",
                "canceled": "❌",
                "expired": "⏰"
            }.get(status['status'], "⚪")
            
            # Build locked participants list
            locked_list = "\n".join([
                f"• {p['phone']} - ✓ Locked"
                for p in status['locked_participants']
            ])
            
            # Build pending participants list
            pending_list = "\n".join([
                f"• {p['phone']} - ⏳ Not locked"
                for p in status['pending_participants']
            ])
            
            # Progress bar
            progress = status['completion_percentage']
            filled = int(progress / 10)
            bar = "█" * filled + "░" * (10 - filled)
            
            response = f"""{status_icon} *{status['title']} Status*

💰 Amount: {status['amount_per_person']} ALGO per person
👥 Organizer: {status['organizer']}
📅 Deadline: {status['deadline'].strftime('%b %d, %Y')} ({status['days_until_deadline']} days left)

📊 *Progress:* {progress}%
[{bar}]

✅ *Locked ({len(status['locked_participants'])}/{status['total_participants']}):*
{locked_list if locked_list else "None yet"}

⏳ *Pending ({len(status['pending_participants'])}):*
{pending_list if pending_list else "All locked! 🎉"}

💰 *Total Locked:* {status['total_locked']} / {status['amount_per_person'] * status['total_participants']} ALGO

{"🚨 *Reminder:* Lock your funds before deadline!" if pending_list else ""}

Lock now: /commit {commitment_id}"""
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get commitment status: {e}")
            return f"❌ Failed to get status: {str(e)}"
    
    def handle_cancel_commitment(
        self,
        db: Session,
        commitment_id: int,
        organizer_phone: str
    ) -> str:
        """
        Cancel commitment and refund all
        
        Example: /cancel 123
        """
        try:
            # Get status first
            status = commitment_service.get_commitment_status(db, commitment_id)
            
            # Cancel and refund
            results = commitment_service.cancel_commitment(
                db=db,
                commitment_id=commitment_id,
                organizer_phone=organizer_phone
            )
            
            refund_list = "\n".join([
                f"• {phone}: ✓ Refunded"
                for phone in results.keys()
            ])
            
            response = f"""❌ *Commitment Canceled*

📋 {status['title']}
💰 Total refunded: {status['total_locked']} ALGO

✅ *Refunds:*
{refund_list if refund_list else "No locked funds to refund"}

All participants have been refunded."""
            
            # Notify all participants
            for phone in results.keys():
                try:
                    notification_service.send_whatsapp_notification(
                        to_phone=phone,
                        message=f"""💸 *Commitment Canceled - Refunded*

{status['title']} was canceled by organizer.

✅ Your {status['amount_per_person']} ALGO has been refunded.

Check balance: /balance"""
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify {phone}: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to cancel commitment: {e}")
            return f"❌ Failed to cancel: {str(e)}"
    
    def handle_add_participant(
        self,
        db: Session,
        commitment_id: int,
        organizer_phone: str,
        participant_phone: str
    ) -> str:
        """
        Add participant to commitment
        
        Example: /add 123 +919999999999
        """
        try:
            # Verify organizer
            status = commitment_service.get_commitment_status(db, commitment_id)
            if status['organizer'] != organizer_phone:
                return "❌ Only organizer can add participants"
            
            # Add participant
            participant = commitment_service.add_participant(
                db=db,
                commitment_id=commitment_id,
                phone=participant_phone
            )
            
            response = f"""✅ *Participant Added*

Added {participant_phone} to:
📋 {status['title']}

They can lock funds with:
/commit {commitment_id}"""
            
            # Notify participant
            try:
                notification_service.send_whatsapp_notification(
                    to_phone=participant_phone,
                    message=f"""💸 *Payment Commitment Invitation*

{organizer_phone} added you to:
📋 {status['title']}

💰 Your share: {status['amount_per_person']} ALGO
📅 Deadline: {status['deadline'].strftime('%b %d, %Y')} ({status['days_until_deadline']} days)

🔒 Lock your funds now:
/commit {commitment_id}

Your funds will be:
• Released to organizer on deadline
• Refunded if canceled

Check status: /commitment {commitment_id}"""
                )
            except Exception as e:
                logger.warning(f"Failed to notify participant: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to add participant: {e}")
            return f"❌ Failed to add participant: {str(e)}"
    
    def handle_reliability(
        self,
        db: Session,
        phone: str
    ) -> str:
        """
        Show user's reliability score
        
        Example: /reliability
        """
        try:
            reliability = commitment_service.get_user_reliability(db, phone)
            
            # Recent commitment list
            recent_list = "\n".join([
                f"• {c['status'].upper()} - {c['amount']} ALGO"
                for c in reliability['recent_commitments'][:5]
            ])
            
            response = f"""👤 *Your Reliability Score*

{reliability['badge']} *Score: {reliability['score']}/100*

📊 *Statistics:*
✅ Fulfilled: {reliability['fulfilled_on_time']}
⚠️ Missed: {reliability['missed']}
📈 Total: {reliability['total_commitments']}

🎯 *Reliability: {reliability['reliability_percentage']}%*

📝 *Recent Commitments:*
{recent_list if recent_list else "No commitments yet"}

{"💡 Keep locking funds on time to improve your score!" if reliability['score'] < 90 else "🌟 Excellent reliability! Keep it up!"}"""
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get reliability: {e}")
            return f"❌ Failed to get reliability: {str(e)}"
    
    def handle_my_commitments(
        self,
        db: Session,
        phone: str
    ) -> str:
        """
        List user's commitments
        
        Example: /my commitments
        """
        try:
            from backend.models.commitment import CommitmentParticipant
            
            # Get all commitments for user
            commitments = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.phone == phone
            ).all()
            
            if not commitments:
                return """📋 *Your Commitments*

No commitments yet.

Create one: /lock create [title] [amount] [people] [days]
Example: /lock create Goa Trip 500 5 7"""
            
            locked = [c for c in commitments if c.is_locked]
            pending = [c for c in commitments if c.status.value == "invited"]
            
            locked_list = "\n".join([
                f"#{c.commitment_id} - {c.amount} ALGO ✓"
                for c in locked[:5]
            ])
            
            pending_list = "\n".join([
                f"#{c.commitment_id} - {c.amount} ALGO ⏳"
                for c in pending[:5]
            ])
            
            response = f"""📋 *Your Commitments*

✅ *Locked ({len(locked)}):*
{locked_list if locked_list else "None"}

⏳ *Pending ({len(pending)}):*
{pending_list if pending_list else "None"}

View details: /commitment [id]
Lock funds: /commit [id]
Check reliability: /reliability"""
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get commitments: {e}")
            return f"❌ Failed to get commitments: {str(e)}"


# Singleton instance
commitment_commands = CommitmentCommands()
