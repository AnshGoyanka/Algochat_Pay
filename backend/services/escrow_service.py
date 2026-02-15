"""
Escrow Service - Handle locked funds for payment commitments
Uses Algorand escrow accounts with time locks
"""
import logging
from datetime import datetime
from typing import Optional, Dict
from algosdk import account, mnemonic
from backend.algorand.client import algorand_client
from backend.config import settings

logger = logging.getLogger(__name__)


class EscrowService:
    """
    Manages escrow accounts for payment commitments
    Funds are locked until deadline, then auto-released
    """
    
    def __init__(self):
        """Initialize service (no client needed, uses algorand_client directly)"""
        pass
    
    def create_escrow_account(self) -> Dict[str, str]:
        """
        Create a new escrow account for a commitment
        
        Returns:
            Dict with address and private_key (for backend control)
        """
        try:
            # Generate new account for escrow
            private_key, address = account.generate_account()
            
            logger.info(f"Created escrow account: {address}")
            
            return {
                "address": address,
                "private_key": private_key,
                "mnemonic": mnemonic.from_private_key(private_key)
            }
            
        except Exception as e:
            logger.error(f"Failed to create escrow account: {e}")
            raise
    
    def lock_funds_to_escrow(
        self,
        participant_private_key: str,
        escrow_address: str,
        amount: float,
        note: str = ""
    ) -> str:
        """
        Lock participant's funds into escrow account
        
        Args:
            participant_private_key: Participant's private key
            escrow_address: Escrow account address
            amount: Amount to lock in ALGO
            note: Transaction note
        
        Returns:
            Transaction ID
        """
        try:
            # Send payment to escrow
            tx_id = algorand_client.send_payment(
                sender_private_key=participant_private_key,
                receiver_address=escrow_address,
                amount_algo=amount,
                note=note
            )
            
            logger.info(f"Locked {amount} ALGO to escrow {escrow_address}: {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to lock funds: {e}")
            raise
    
    def release_escrow_to_organizer(
        self,
        escrow_private_key: str,
        organizer_address: str,
        amount: float,
        note: str = ""
    ) -> str:
        """
        Release locked funds from escrow to organizer
        Called when deadline passes or commitment is fulfilled
        
        Args:
            escrow_private_key: Escrow account private key
            organizer_address: Organizer's wallet address
            amount: Amount to release in ALGO
            note: Transaction note
        
        Returns:
            Transaction ID
        """
        try:
            # Send from escrow to organizer
            tx_id = algorand_client.send_payment(
                sender_private_key=escrow_private_key,
                receiver_address=organizer_address,
                amount_algo=amount,
                note=note
            )
            
            logger.info(f"Released {amount} ALGO to organizer {organizer_address}: {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to release escrow: {e}")
            raise
    
    def refund_from_escrow(
        self,
        escrow_private_key: str,
        participant_address: str,
        amount: float,
        note: str = ""
    ) -> str:
        """
        Refund locked funds back to participant
        Called when commitment is canceled
        
        Args:
            escrow_private_key: Escrow account private key
            participant_address: Participant's wallet address
            amount: Amount to refund in ALGO
            note: Transaction note
        
        Returns:
            Transaction ID
        """
        try:
            # Send from escrow back to participant
            tx_id = algorand_client.send_payment(
                sender_private_key=escrow_private_key,
                receiver_address=participant_address,
                amount_algo=amount,
                note=note
            )
            
            logger.info(f"Refunded {amount} ALGO to participant {participant_address}: {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to refund: {e}")
            raise
    
    def get_escrow_balance(self, escrow_address: str) -> float:
        """
        Get current balance of escrow account
        
        Args:
            escrow_address: Escrow account address
        
        Returns:
            Balance in ALGO
        """
        try:
            balance = algorand_client.get_balance(escrow_address)
            return balance
        except Exception as e:
            logger.error(f"Failed to get escrow balance: {e}")
            return 0.0
    
    def validate_escrow_balance(
        self,
        escrow_address: str,
        expected_amount: float
    ) -> bool:
        """
        Validate that escrow has expected amount
        
        Args:
            escrow_address: Escrow account address
            expected_amount: Expected balance in ALGO
        
        Returns:
            True if balance matches (within 0.01 ALGO tolerance)
        """
        try:
            actual_balance = self.get_escrow_balance(escrow_address)
            # Allow 0.01 ALGO difference for transaction fees
            return abs(actual_balance - expected_amount) < 0.01
        except Exception as e:
            logger.error(f"Failed to validate escrow balance: {e}")
            return False
    
    def batch_release_to_organizer(
        self,
        escrow_private_key: str,
        escrow_address: str,
        organizer_address: str,
        note: str = ""
    ) -> str:
        """
        Release ALL funds from escrow to organizer at once
        Used when deadline passes and commitment completes
        
        Args:
            escrow_private_key: Escrow account private key
            escrow_address: Escrow account address
            organizer_address: Organizer's wallet address
            note: Transaction note
        
        Returns:
            Transaction ID
        """
        try:
            # Get total balance
            balance = self.get_escrow_balance(escrow_address)
            
            if balance <= 0.001:  # Account for min balance
                raise ValueError("No funds to release in escrow")
            
            # Release all (minus transaction fee)
            release_amount = balance - 0.001
            
            tx_id = self.release_escrow_to_organizer(
                escrow_private_key=escrow_private_key,
                organizer_address=organizer_address,
                amount=release_amount,
                note=note
            )
            
            logger.info(f"Batch released {release_amount} ALGO to organizer")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to batch release: {e}")
            raise
    
    def batch_refund_to_participants(
        self,
        escrow_private_key: str,
        participants: list,
        note: str = ""
    ) -> Dict[str, str]:
        """
        Refund all participants when commitment is canceled
        
        Args:
            escrow_private_key: Escrow account private key
            participants: List of dicts with 'address' and 'amount'
            note: Transaction note
        
        Returns:
            Dict mapping participant address to transaction ID
        """
        results = {}
        
        for participant in participants:
            try:
                tx_id = self.refund_from_escrow(
                    escrow_private_key=escrow_private_key,
                    participant_address=participant['address'],
                    amount=participant['amount'],
                    note=note
                )
                results[participant['address']] = tx_id
                
            except Exception as e:
                logger.error(f"Failed to refund {participant['address']}: {e}")
                results[participant['address']] = f"ERROR: {str(e)}"
        
        return results


# Singleton instance
escrow_service = EscrowService()
