"""
Telegram webhook handler
Processes incoming messages from Telegram Bot API
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import logging

from backend.database import get_db
from backend.config import settings
from backend.services import wallet_service, payment_service, ticket_service, fund_service
from backend.services.split_service import split_service
from backend.services.contact_service import contact_service
from backend.services.nl_mapper import nl_mapper
from bot.command_parser import command_parser, CommandType, ParsedCommand
from bot.response_templates import response_templates
from bot.button_menus import button_menus

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple in-memory storage for chat_id to phone mapping
# TODO: Move to database table for production
telegram_user_registry = {}


class TelegramBot:
    """
    Telegram bot logic handler
    Shares command processing with WhatsApp bot
    """
    
    def __init__(self):
        self.parser = command_parser
        self.templates = response_templates
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(self, chat_id: str, text: str, keyboard=None, reply_keyboard=None):
        """
        Send message via Telegram Bot API with optional keyboards
        
        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            keyboard: Inline keyboard markup (for one-time button actions)
            reply_keyboard: Reply keyboard markup (persistent buttons at bottom)
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
                
                # Add inline keyboard if provided
                if keyboard:
                    payload["reply_markup"] = keyboard
                # Or add reply keyboard if provided
                elif reply_keyboard:
                    payload["reply_markup"] = reply_keyboard
                
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
                raise
    
    def process_button_callback(self, db: Session, chat_id: str, user_phone: str, callback_data: str) -> str:
        """
        Process button callback (when user clicks a button)
        
        Args:
            db: Database session
            chat_id: Telegram chat ID
            user_phone: User's phone number
            callback_data: Button callback data (command ID)
            
        Returns:
            Response text to send back
        """
        logger.info(f"Processing button callback: {callback_data}")
        
        # Map button IDs to command text
        command_map = {
            "balance": "balance",
            "history": "history",
            "help": "help",
            "menu": "menu",
            "list_events": "events",
            "list_funds": "funds",
            "my_splits": "my splits",
            "my_tickets": "my tickets",
            "demo_stats": "demo stats"
        }
        
        # Get the command text
        command_text = command_map.get(callback_data, callback_data)
        
        # Process as regular message
        return self.process_message(db, chat_id, user_phone, command_text)
    
    def process_message(self, db: Session, chat_id: str, user_phone: str, message_text: str) -> str:
        """
        Process incoming Telegram message
        
        Args:
            db: Database session
            chat_id: Telegram chat ID (used as unique identifier)
            user_phone: User's phone number (from Telegram profile or manual input)
            message_text: Message text
        
        Returns:
            Response text to send back
        """
        logger.info(f"Processing Telegram message from chat {chat_id}: {message_text[:50]}")
        
        # Try natural language parsing first
        nl_result = nl_mapper.parse_natural_language(message_text)
        
        if nl_result and nl_result.confidence > 0.8:
            # Convert nl_mapper result to ParsedCommand
            logger.info(f"Natural language match: {nl_result.command} (confidence: {nl_result.confidence})")
            try:
                command_type = CommandType(nl_result.command.lower())
            except ValueError:
                # Fallback if command type doesn't match
                command_type = CommandType.UNKNOWN
            
            cmd = ParsedCommand(command_type, nl_result.params, nl_result.original_text)
        else:
            # Fallback to traditional command parser
            cmd = self.parser.parse(message_text)
        
        try:
            # Route to appropriate handler
            if cmd.type == CommandType.HELP:
                return self.parser.get_help_text()
            
            elif cmd.type == CommandType.MENU:
                return self.templates.quick_menu()
            
            elif cmd.type == CommandType.BALANCE:
                return self._handle_balance(db, user_phone)
            
            elif cmd.type == CommandType.PAY:
                return self._handle_payment(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.SPLIT:
                return self._handle_split(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.PAY_SPLIT:
                return self._handle_pay_split(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.VIEW_SPLIT:
                return self._handle_view_split(db, cmd.params)
            
            elif cmd.type == CommandType.MY_SPLITS:
                return self._handle_my_splits(db, user_phone)
            
            elif cmd.type == CommandType.CREATE_FUND:
                return self._handle_create_fund(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.CONTRIBUTE:
                return self._handle_contribute(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.VIEW_FUND:
                return self._handle_view_fund(db, cmd.params)
            
            elif cmd.type == CommandType.LIST_FUNDS:
                return self._handle_list_funds(db)
            
            elif cmd.type == CommandType.BUY_TICKET:
                return self._handle_buy_ticket(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.VERIFY_TICKET:
                return self._handle_verify_ticket(db, cmd.params)
            
            elif cmd.type == CommandType.MY_TICKETS:
                return self._handle_my_tickets(db, user_phone)
            
            elif cmd.type == CommandType.LIST_EVENTS:
                return self._handle_list_events(db)
            
            elif cmd.type == CommandType.HISTORY:
                return self._handle_history(db, user_phone)
            
            elif cmd.type == CommandType.DEMO_STATS:
                return self._handle_demo_stats(db)
            
            # Contacts
            elif cmd.type == CommandType.SAVE_CONTACT:
                return self._handle_save_contact(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.REMOVE_CONTACT:
                return self._handle_remove_contact(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.MY_CONTACTS:
                return self._handle_my_contacts(db, user_phone)
            
            elif cmd.type == CommandType.SET_NAME:
                return self._handle_set_name(db, user_phone, cmd.params)
            
            elif cmd.type == CommandType.PAY_NAME:
                return self._handle_pay_by_name(db, user_phone, cmd.params)
            
            else:
                return self.templates.unknown_command(message_text)
        
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return self.templates.error_message("general", str(e))
        
        except Exception as e:
            logger.error(f"Error processing Telegram message: {e}", exc_info=True)
            return self.templates.error_message("general", "Something went wrong. Please try again.")
    
    def _handle_balance(self, db: Session, phone: str) -> str:
        """Handle balance command"""
        # Get or create wallet
        user, created = wallet_service.get_or_create_wallet(db, phone)
        
        if created:
            # New user - send welcome message
            balance = wallet_service.get_balance(db, phone)
            return self.templates.welcome_new_user(user.wallet_address, balance)
        
        # Existing user - send balance
        wallet_info = wallet_service.get_wallet_info(db, phone)
        return self.templates.balance_info(
            wallet_info["phone"],
            wallet_info["address"],
            wallet_info["balance"]
        )
    
    def _handle_payment(self, db: Session, sender_phone: str, params: dict) -> str:
        """Handle payment command"""
        receiver_phone = params["receiver_phone"]
        amount = params["amount"]
        
        # Execute payment
        transaction = payment_service.send_payment(
            db=db,
            sender_phone=sender_phone,
            receiver_phone=receiver_phone,
            amount=amount,
            note="Telegram payment"
        )
        
        # Get new balance
        new_balance = wallet_service.get_balance(db, sender_phone)
        
        # Get merchant info if exists
        from backend.services.merchant_service import merchant_service
        merchant_name = None
        if transaction.merchant_id:
            merchant = merchant_service.get_merchant_by_id(db, transaction.merchant_id)
            merchant_name = merchant.merchant_name if merchant else None
        
        return self.templates.payment_success(
            receiver_phone,
            amount,
            transaction.tx_id,
            new_balance,
            transaction.payment_ref,
            merchant_name
        )
    
    def _handle_pay_by_name(self, db: Session, sender_phone: str, params: dict) -> str:
        """Handle payment by contact name"""
        name = params.get("name", "")
        amount = params.get("amount")
        
        if not name or not amount:
            return "\u274c Please specify a name and amount. Example: `pay ansh 50`"
        
        amount = float(amount)
        
        # Resolve name to phone number
        resolved_phone, display_info = contact_service.resolve_name(db, sender_phone, name)
        
        if not resolved_phone:
            return display_info
        
        # Execute payment using resolved phone
        transaction = payment_service.send_payment(
            db=db,
            sender_phone=sender_phone,
            receiver_phone=resolved_phone,
            amount=amount,
            note=f"Telegram payment to {name}"
        )
        
        new_balance = wallet_service.get_balance(db, sender_phone)
        
        return self.templates.payment_success(
            resolved_phone,
            amount,
            transaction.tx_id,
            new_balance,
            transaction.payment_ref,
            name.title()
        )
    
    def _handle_save_contact(self, db: Session, phone: str, params: dict) -> str:
        """Handle save contact command"""
        nickname = params.get("nickname", "")
        contact_phone = params.get("contact_phone", "")
        
        try:
            contact = contact_service.save_contact(db, phone, nickname, contact_phone)
            return self.templates.contact_saved(contact.nickname, contact.contact_phone)
        except ValueError as e:
            return f"\u274c {str(e)}"
    
    def _handle_remove_contact(self, db: Session, phone: str, params: dict) -> str:
        """Handle remove contact command"""
        nickname = params.get("nickname", "")
        
        removed = contact_service.remove_contact(db, phone, nickname)
        if removed:
            return self.templates.contact_removed(nickname)
        else:
            return f"\u274c No contact named *\"{nickname}\"* found."
    
    def _handle_my_contacts(self, db: Session, phone: str) -> str:
        """Handle list contacts command"""
        contacts = contact_service.list_contacts(db, phone)
        return self.templates.contact_list(contacts)
    
    def _handle_set_name(self, db: Session, phone: str, params: dict) -> str:
        """Handle set display name command"""
        name = params.get("name", "")
        
        if not name:
            return "\u274c Please provide a name. Example: `set name Ansh`"
        
        try:
            wallet_service.get_or_create_wallet(db, phone)
            user = contact_service.set_display_name(db, phone, name)
            return self.templates.name_set(user.display_name)
        except ValueError as e:
            return f"\u274c {str(e)}"
    
    def _handle_split(self, db: Session, initiator_phone: str, params: dict) -> str:
        """Handle bill split command"""
        total_amount = params["amount"]
        description = params["description"]
        participants = params["participants"]
        
        # Create split bill
        split_bill = split_service.create_split_bill(
            db=db,
            initiator_phone=initiator_phone,
            total_amount=total_amount,
            description=description,
            participant_phones=participants
        )
        
        return self.templates.split_initiated(
            split_bill.id,
            total_amount,
            split_bill.amount_per_person,
            participants,
            description
        )
    
    def _handle_pay_split(self, db: Session, phone: str, params: dict) -> str:
        """Handle paying share of split bill"""
        split_bill_id = params["split_bill_id"]
        
        result = split_service.pay_split_share(
            db=db,
            split_bill_id=split_bill_id,
            participant_phone=phone
        )
        
        # Get transaction for payment_ref
        from backend.models.transaction import Transaction
        transaction = db.query(Transaction).filter(Transaction.tx_id == result["tx_id"]).first()
        payment_ref = transaction.payment_ref if transaction else None
        
        return self.templates.split_payment_success(
            result["split_bill_id"],
            result["amount_paid"],
            result["tx_id"],
            result["is_fully_paid"],
            result["total_collected"],
            result["total_amount"],
            payment_ref
        )
    
    def _handle_view_split(self, db: Session, params: dict) -> str:
        """Handle view split details"""
        split_bill_id = params["split_bill_id"]
        split_info = split_service.get_split_bill_details(db, split_bill_id)
        return self.templates.split_details(split_info)
    
    def _handle_my_splits(self, db: Session, phone: str) -> str:
        """Handle list my split bills"""
        splits = split_service.get_my_split_bills(db, phone)
        return self.templates.my_splits(splits)
    
    def _handle_create_fund(self, db: Session, creator_phone: str, params: dict) -> str:
        """Handle fund creation"""
        title = params["title"]
        goal_amount = params["goal_amount"]
        
        fund = fund_service.create_fund(
            db=db,
            creator_phone=creator_phone,
            title=title,
            goal_amount=goal_amount
        )
        
        return self.templates.fund_created(
            fund.id,
            fund.title,
            fund.goal_amount,
            fund.deadline
        )
    
    def _handle_contribute(self, db: Session, contributor_phone: str, params: dict) -> str:
        """Handle fund contribution"""
        fund_id = params["fund_id"]
        amount = params["amount"]
        
        contribution = fund_service.contribute_to_fund(
            db=db,
            fund_id=fund_id,
            contributor_phone=contributor_phone,
            amount=amount
        )
        
        # Get updated fund info
        fund = fund_service.get_fund_by_id(db, fund_id)
        
        # Get transaction for payment_ref
        from backend.models.transaction import Transaction
        transaction = db.query(Transaction).filter(Transaction.tx_id == contribution.tx_id).first()
        
        # Get merchant/beneficiary info
        from backend.services.merchant_service import merchant_service
        beneficiary_name = None
        if transaction and transaction.merchant_id:
            merchant = merchant_service.get_merchant_by_id(db, transaction.merchant_id)
            beneficiary_name = merchant.merchant_name if merchant else None
        
        return self.templates.contribution_success(
            fund.title,
            amount,
            fund.current_amount,
            fund.goal_amount,
            contribution.tx_id,
            transaction.payment_ref if transaction else None,
            beneficiary_name
        )
    
    def _handle_view_fund(self, db: Session, params: dict) -> str:
        """Handle view fund details"""
        fund_id = params["fund_id"]
        fund = fund_service.get_fund_by_id(db, fund_id)
        
        if not fund:
            return "❌ Fund not found"
        
        return self.templates.fund_details(fund)
    
    def _handle_buy_ticket(self, db: Session, buyer_phone: str, params: dict) -> str:
        """Handle ticket purchase"""
        # Support both event ID and event name
        event_id = params.get("event_id")
        event_name = params.get("event_name")
        
        # Use the new purchase_ticket method that integrates with Event model
        result = ticket_service.purchase_ticket(
            db=db,
            buyer_phone=buyer_phone,
            event_name=event_name,
            event_id=event_id
        )
        
        # Get event for organizer info
        from backend.models.event import Event
        event = db.query(Event).filter(
            Event.id == event_id if event_id else Event.name == event_name
        ).first()
        organizer_name = event.organizer if event and event.organizer else None
        
        return self.templates.ticket_purchased(
            result["ticket_number"],
            result["event_name"],
            result["ticket_price"],
            result["venue"],
            result["event_date"],
            result["remaining_tickets"],
            result["tx_id"],
            organizer_name,
            None  # payment_ref not available for ticket purchase yet
        )
    
    def _handle_verify_ticket(self, db: Session, params: dict) -> str:
        """Handle ticket verification"""
        ticket_id = params["ticket_id"]
        
        ticket = ticket_service.get_ticket_by_id(db, ticket_id)
        
        if not ticket:
            return "❌ Ticket not found"
        
        is_valid = ticket_service.verify_ticket(db, ticket_id)
        
        return self.templates.ticket_verification(ticket, is_valid)
    
    def _handle_my_tickets(self, db: Session, phone: str) -> str:
        """Handle list user's tickets"""
        tickets = ticket_service.get_user_tickets(db, phone)
        
        return self.templates.user_tickets(tickets)
    
    def _handle_list_events(self, db: Session) -> str:
        """Handle list available events"""
        events = ticket_service.list_events(db)
        
        return self.templates.event_list(events)
    
    def _handle_list_funds(self, db: Session) -> str:
        """Handle list active fundraising campaigns"""
        funds = fund_service.list_active_funds(db)
        
        return self.templates.fund_list(funds)
    
    def _handle_history(self, db: Session, phone: str) -> str:
        """Handle transaction history"""
        transactions = payment_service.get_transaction_history(db, phone, limit=10)
        
        return self.templates.transaction_history(transactions)
    
    def _handle_demo_stats(self, db: Session) -> str:
        """Handle demo statistics"""
        stats = payment_service.get_platform_stats(db)
        
        return self.templates.demo_statistics(stats)


# Bot instance
telegram_bot = TelegramBot()


@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Telegram webhook endpoint
    Receives updates from Telegram Bot API
    """
    try:
        # Parse incoming update
        update = await request.json()
        logger.info(f"Received Telegram update: {update}")
        
        # Handle callback query (button clicks)
        if "callback_query" in update:
            callback_query = update["callback_query"]
            chat_id = str(callback_query["message"]["chat"]["id"])
            callback_id = callback_query["id"]
            callback_data = callback_query["data"]
            
            # Check if user is registered
            user_phone = telegram_user_registry.get(chat_id)
            
            if not user_phone:
                # Answer callback query
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{telegram_bot.api_url}/answerCallbackQuery",
                        json={
                            "callback_query_id": callback_id,
                            "text": "Please register first using /register +1234567890"
                        }
                    )
                return JSONResponse({"ok": True})
            
            # Process button callback
            response_text = telegram_bot.process_button_callback(db, chat_id, user_phone, callback_data)
            
            # Send response with keyboard
            keyboard = button_menus.get_telegram_keyboard(button_menus.MAIN_MENU + button_menus.QUICK_ACTIONS, columns=3)
            await telegram_bot.send_message(chat_id, response_text, keyboard=keyboard)
            
            # Answer callback query to remove loading state
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{telegram_bot.api_url}/answerCallbackQuery",
                    json={"callback_query_id": callback_id}
                )
            
            return JSONResponse({"ok": True})
        
        # Extract message data
        if "message" not in update:
            return JSONResponse({"ok": True})
        
        message = update["message"]
        chat_id = str(message["chat"]["id"])
        
        # Get message text
        text = message.get("text", "")
        if not text:
            await telegram_bot.send_message(chat_id, "Please send a text message.")
            return JSONResponse({"ok": True})
        
        # Handle /start command
        if text == "/start":
            response_text = (
                "🏦 *Welcome to AlgoChat Pay!*\n\n"
                "To get started, please register your phone number:\n\n"
                "Type: `/register +1234567890`\n\n"
                "Replace with your actual phone number with country code.\n\n"
                "After registration, you can:\n"
                "• Check balance\n"
                "• Send ALGO payments\n"
                "• View transaction history\n"
                "• And much more!\n\n"
                "Type `help` after registering to see all commands."
            )
            await telegram_bot.send_message(chat_id, response_text)
            return JSONResponse({"ok": True})
        
        # Handle /register command
        if text.startswith("/register "):
            user_phone = text.replace("/register ", "").strip()
            
            # Validate phone number format (basic validation)
            if not user_phone or len(user_phone) < 10:
                await telegram_bot.send_message(
                    chat_id,
                    "❌ Invalid phone number format.\n\nPlease use: `/register +1234567890`\n\n"
                    "Include country code (e.g., +1 for US, +91 for India)"
                )
                return JSONResponse({"ok": True})
            
            # Store chat_id to phone mapping
            telegram_user_registry[chat_id] = user_phone
            
            # Create quick action keyboard for new users
            keyboard = button_menus.get_telegram_keyboard(button_menus.MAIN_MENU + button_menus.QUICK_ACTIONS, columns=3)
            
            response_text = (
                f"✅ *Registration Successful!*\n\n"
                f"📱 Phone: `{user_phone}`\n\n"
                f"You're all set! Click a button below or type commands:\n\n"
                f"• `balance` - Check your ALGO balance\n"
                f"• `history` - View transactions\n"
                f"• `help` - See all commands\n\n"
                f"Your Algorand wallet will be created automatically on first use! 🚀"
            )
            await telegram_bot.send_message(chat_id, response_text, keyboard=keyboard)
            return JSONResponse({"ok": True})
        
        # Check if user is registered
        user_phone = telegram_user_registry.get(chat_id)
        
        if not user_phone:
            # Check if they shared contact
            contact = message.get("contact")
            if contact:
                user_phone = contact.get("phone_number")
                if user_phone:
                    telegram_user_registry[chat_id] = user_phone
                    
                    # Send keyboard with registration confirmation
                    keyboard = button_menus.get_telegram_keyboard(button_menus.MAIN_MENU + button_menus.QUICK_ACTIONS, columns=3)
                    
                    response_text = (
                        f"✅ *Registration Successful!*\n\n"  
                        f"📱 Phone: `{user_phone}`\n\n"
                        f"Click a button below to get started!"
                    )
                    await telegram_bot.send_message(chat_id, response_text, keyboard=keyboard)
                    return JSONResponse({"ok": True})
            
            # Not registered
            await telegram_bot.send_message(
                chat_id,
                "⚠️ *Please register first!*\n\n"
                "Type: `/register +1234567890`\n\n"
                "Or send `/start` for more info."
            )
            return JSONResponse({"ok": True})
        
        # Process the command
        response_text = telegram_bot.process_message(db, chat_id, user_phone, text)
        
        # Add keyboard to response for static commands
        static_commands = ["help", "balance", "history", "menu", "events", "funds", "my splits", "my tickets", "my contacts", "my commitments", "reliability"]
        should_add_keyboard = any(cmd in text.lower() for cmd in static_commands)
        
        if should_add_keyboard:
            keyboard = button_menus.get_telegram_keyboard(button_menus.MAIN_MENU + button_menus.QUICK_ACTIONS, columns=3)
            await telegram_bot.send_message(chat_id, response_text, keyboard=keyboard)
        else:
            # For transaction commands, don't clutter with keyboards
            await telegram_bot.send_message(chat_id, response_text)
        
        return JSONResponse({"ok": True})
    
    except Exception as e:
        logger.error(f"Error in Telegram webhook: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/webhook/telegram")
async def telegram_webhook_verify(request: Request):
    """
    Verification endpoint for Telegram webhook
    """
    return {"status": "Telegram webhook is active", "bot": "AlgoChat Pay"}
