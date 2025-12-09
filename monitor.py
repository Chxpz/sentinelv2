#!/usr/bin/env python3
"""
Transaction Monitoring Service (Example/Placeholder)

In production, this service would:
1. Monitor Safe Transaction Service API for pending transactions
2. Listen to blockchain events for Safe transactions
3. Automatically notify users via Telegram when pending tx is detected

For this MVP, it's a placeholder that can be triggered manually via CLI or API.
"""
import asyncio
import logging
from typing import List, Dict, Any
from database import db
from telegram_bot import telegram_bot
from safe_service import safe_service
from config import settings

logger = logging.getLogger(__name__)


class TransactionMonitor:
    """Monitor Safe wallets for pending transactions"""
    
    def __init__(self):
        self.monitoring = False
        self.check_interval = 30  # seconds
    
    async def start_monitoring(self):
        """Start monitoring all registered Safe wallets"""
        self.monitoring = True
        logger.info("Transaction monitor started")
        
        while self.monitoring:
            try:
                await self.check_all_safes()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("Transaction monitor stopped")
    
    async def check_all_safes(self):
        """Check all registered Safes for pending transactions"""
        # In production, you would:
        # 1. Query database for all active Safes
        # 2. For each Safe, query the Safe Transaction Service
        # 3. Check for pending transactions
        # 4. Notify users about new pending transactions
        
        # For MVP, this is a placeholder
        # Actual implementation would query:
        # https://safe-transaction-mainnet.safe.global/api/v1/safes/{address}/multisig-transactions/
        
        logger.debug("Checking for pending transactions...")
    
    async def check_safe(self, safe_address: str) -> List[Dict[str, Any]]:
        """
        Check a specific Safe for pending transactions
        
        In production, this would query the Safe Transaction Service API:
        GET https://safe-transaction-{network}.safe.global/api/v1/safes/{address}/multisig-transactions/
        
        Returns list of pending transactions
        """
        try:
            # Use the safe_service to check pending transactions
            pending_txs = safe_service.check_pending_transactions(safe_address)
            
            if pending_txs:
                logger.info(f"Found {len(pending_txs)} pending transactions for {safe_address}")
            
            return pending_txs
            
        except Exception as e:
            logger.error(f"Error checking Safe {safe_address}: {e}")
            return []
    
    async def handle_pending_transaction(
        self,
        safe_address: str,
        tx_data: Dict[str, Any]
    ):
        """Handle a newly detected pending transaction"""
        try:
            # Get Safe info from database
            safe = await db.get_safe_by_address(safe_address)
            if not safe:
                logger.warning(f"Safe not found in database: {safe_address}")
                return
            
            # Extract transaction details
            to = tx_data.get('to', '')
            value = tx_data.get('value', 0)
            data = tx_data.get('data', '0x')
            tx_hash = tx_data.get('safeTxHash', '')
            
            # Check if we've already notified about this transaction
            # (In production, track this in database)
            
            # Create transaction record
            await db.create_transaction_record(
                safe_address=safe_address,
                tx_hash=tx_hash,
                to_address=to,
                value=str(value),
                data=data,
                status="pending"
            )
            
            # Send Telegram notification
            await telegram_bot.notify_pending_transaction(
                telegram_id=safe['telegram_id'],
                tx_id=tx_hash,
                safe_address=safe_address,
                to=to,
                value=value,
                data=data
            )
            
            logger.info(f"Notified user about transaction {tx_hash}")
            
        except Exception as e:
            logger.error(f"Error handling pending transaction: {e}")


# Global monitor instance
transaction_monitor = TransactionMonitor()


# Example of how to integrate with a webhook or event listener
async def webhook_handler(safe_address: str, transaction_data: Dict[str, Any]):
    """
    Example webhook handler for Safe Transaction Service webhooks
    
    In production, you would:
    1. Set up a webhook endpoint in your API
    2. Register webhook with Safe Transaction Service
    3. Receive notifications when new transactions are proposed
    4. Call this handler to process them
    """
    logger.info(f"Received webhook for Safe {safe_address}")
    await transaction_monitor.handle_pending_transaction(
        safe_address=safe_address,
        tx_data=transaction_data
    )


# Example of how to poll for transactions
async def poll_safe_transactions(safe_address: str):
    """
    Example polling function
    
    In production, you might use this in addition to webhooks
    as a fallback mechanism
    """
    while True:
        pending_txs = await transaction_monitor.check_safe(safe_address)
        
        for tx in pending_txs:
            await transaction_monitor.handle_pending_transaction(
                safe_address=safe_address,
                tx_data=tx
            )
        
        await asyncio.sleep(30)


if __name__ == "__main__":
    """
    Example standalone monitoring script
    This could be run as a separate service
    """
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        logger.info("Starting transaction monitor...")
        await transaction_monitor.start_monitoring()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
