"""
Algorand blockchain client wrapper
Handles connection to Algorand network with fallback support
"""
from algosdk.v2client import algod, indexer
from algosdk import account, mnemonic
from algosdk.transaction import PaymentTxn, AssetConfigTxn, AssetTransferTxn, wait_for_confirmation
from typing import Dict, Optional, Tuple
import logging
from backend.config import settings
from backend.utils.demo_safety import AlgorandNodeFallback, with_retry, RetryConfig

logger = logging.getLogger(__name__)


class AlgorandClient:
    """
    Wrapper for Algorand SDK with fallback support
    Provides clean interface for wallet and transaction operations
    """
    
    def __init__(self):
        # Primary node
        self.algod_client = algod.AlgodClient(
            settings.ALGORAND_ALGOD_TOKEN,
            settings.ALGORAND_ALGOD_ADDRESS
        )
        
        self.indexer_client = indexer.IndexerClient(
            settings.ALGORAND_INDEXER_TOKEN,
            settings.ALGORAND_INDEXER_ADDRESS
        )
        
        # Setup fallback system with backup nodes
        backup_nodes = [
            "https://testnet-api.4160.nodely.io",  # Nodely backup
            "https://testnet-algorand.api.purestake.io/ps2"  # PureStake backup (requires API key)
        ]
        self.node_fallback = AlgorandNodeFallback(
            primary_node=settings.ALGORAND_ALGOD_ADDRESS,
            backup_nodes=backup_nodes
        )
        
        logger.info(f"Connected to Algorand {settings.ALGORAND_NETWORK}")
        logger.info(f"Primary node: {settings.ALGORAND_ALGOD_ADDRESS}")
        logger.info(f"Backup nodes configured: {len(backup_nodes)}")
    
    @with_retry(RetryConfig(max_attempts=3, initial_delay=0.5))
    def get_balance(self, address: str) -> float:
        """
        Get ALGO balance for an address (with retry)
        
        Args:
            address: Algorand address
        
        Returns:
            Balance in ALGO (not microALGOs)
        """
        try:
            account_info = self.algod_client.account_info(address)
            balance_microalgos = account_info.get("amount", 0)
            self.node_fallback.record_success()
            return balance_microalgos / 1_000_000  # Convert to ALGO
        except Exception as e:
            self.node_fallback.record_failure()
            logger.error(f"Failed to get balance for {address}: {e}")
            raise
    
    def create_wallet(self) -> Tuple[str, str, str]:
        """
        Create new Algorand wallet
        
        Returns:
            (private_key, wallet_address, mnemonic_phrase)
        """
        private_key, address = account.generate_account()
        mnemonic_phrase = mnemonic.from_private_key(private_key)
        
        logger.info(f"Created wallet: {address}")
        return private_key, address, mnemonic_phrase
    
    @with_retry(RetryConfig(max_attempts=3, initial_delay=1.0))
    def send_payment(
        self,
        sender_private_key: str,
        receiver_address: str,
        amount_algo: float,
        note: str = ""
    ) -> str:
        """
        Send ALGO payment (with retry and fallback)
        
        Args:
            sender_private_key: Sender's private key (for signing)
            receiver_address: Recipient's address
            amount_algo: Amount in ALGO
            note: Optional transaction note
        
        Returns:
            Transaction ID
        """
        try:
            # Get sender address from private key
            sender_address = account.address_from_private_key(sender_private_key)
            
            # Get suggested params
            params = self.algod_client.suggested_params()
            
            # Convert ALGO to microALGOs
            amount_microalgos = int(amount_algo * 1_000_000)
            
            # Create payment transaction
            txn = PaymentTxn(
                sender=sender_address,
                sp=params,
                receiver=receiver_address,
                amt=amount_microalgos,
                note=note.encode() if note else None
            )
            
            # Sign transaction
            signed_txn = txn.sign(sender_private_key)
            
            # Send transaction
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
            
            self.node_fallback.record_success()
            logger.info(f"Payment sent: {tx_id} ({amount_algo} ALGO)")
            return tx_id
            
        except Exception as e:
            self.node_fallback.record_failure()
            logger.error(f"Payment failed: {e}")
            raise
    
    def create_nft_asset(
        self,
        creator_private_key: str,
        asset_name: str,
        unit_name: str,
        total: int = 1,
        metadata_url: str = ""
    ) -> int:
        """
        Create NFT as Algorand Standard Asset (ASA)
        
        Args:
            creator_private_key: Creator's private key
            asset_name: Asset display name
            unit_name: Short asset ticker
            total: Total supply (1 for unique NFT)
            metadata_url: IPFS or HTTP URL for metadata
        
        Returns:
            Asset ID
        """
        try:
            creator_address = account.address_from_private_key(creator_private_key)
            params = self.algod_client.suggested_params()
            
            txn = AssetConfigTxn(
                sender=creator_address,
                sp=params,
                total=total,
                default_frozen=False,
                unit_name=unit_name,
                asset_name=asset_name,
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                url=metadata_url,
                decimals=0
            )
            
            signed_txn = txn.sign(creator_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
            
            # Get asset ID from confirmed transaction
            asset_id = confirmed_txn["asset-index"]
            
            logger.info(f"Created NFT asset: {asset_id} ({asset_name})")
            return asset_id
            
        except Exception as e:
            logger.error(f"NFT creation failed: {e}")
            raise
    
    def transfer_asset(
        self,
        sender_private_key: str,
        receiver_address: str,
        asset_id: int,
        amount: int = 1
    ) -> str:
        """
        Transfer ASA (including NFT tickets)
        
        Args:
            sender_private_key: Sender's private key
            receiver_address: Recipient's address
            asset_id: Asset ID to transfer
            amount: Amount to transfer
        
        Returns:
            Transaction ID
        """
        try:
            sender_address = account.address_from_private_key(sender_private_key)
            params = self.algod_client.suggested_params()
            
            txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=receiver_address,
                amt=amount,
                index=asset_id
            )
            
            signed_txn = txn.sign(sender_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            logger.info(f"Asset transferred: Asset {asset_id}, TX {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Asset transfer failed: {e}")
            raise
    
    def opt_in_asset(self, account_private_key: str, asset_id: int) -> str:
        """
        Opt-in to receive an asset (required before receiving ASAs)
        
        Args:
            account_private_key: Account's private key
            asset_id: Asset ID to opt into
        
        Returns:
            Transaction ID
        """
        try:
            account_address = account.address_from_private_key(account_private_key)
            params = self.algod_client.suggested_params()
            
            # Opt-in is a 0-amount transfer to self
            txn = AssetTransferTxn(
                sender=account_address,
                sp=params,
                receiver=account_address,
                amt=0,
                index=asset_id
            )
            
            signed_txn = txn.sign(account_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            logger.info(f"Opted into asset {asset_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Asset opt-in failed: {e}")
            raise
    
    def get_account_assets(self, address: str) -> list:
        """
        Get all assets held by an account
        
        Args:
            address: Algorand address
        
        Returns:
            List of asset holdings
        """
        try:
            account_info = self.algod_client.account_info(address)
            return account_info.get("assets", [])
        except Exception as e:
            logger.error(f"Failed to get assets for {address}: {e}")
            return []
    
    def get_transaction_info(self, tx_id: str) -> Optional[Dict]:
        """
        Get transaction details by ID
        
        Args:
            tx_id: Transaction ID
        
        Returns:
            Transaction info dict or None
        """
        try:
            return self.algod_client.pending_transaction_info(tx_id)
        except Exception as e:
            logger.error(f"Failed to get transaction {tx_id}: {e}")
            return None


# Global client instance
algorand_client = AlgorandClient()
