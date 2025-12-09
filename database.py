from supabase import create_client, Client
from config import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database interface using Supabase"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def create_safe(
        self,
        telegram_id: str,
        safe_address: str,
        owner1_address: str,
        owner2_address: str,
        agent_address: str
    ) -> Dict[str, Any]:
        """Create a new Safe record in the database"""
        try:
            data = {
                "telegram_id": telegram_id,
                "safe_address": safe_address,
                "owner1_address": owner1_address,
                "owner2_address": owner2_address,
                "agent_address": agent_address,
                "status": "active"
            }
            result = self.client.table("safes").insert(data).execute()
            logger.info(f"Created Safe record: {safe_address}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error creating Safe: {e}")
            raise
    
    async def get_safe_by_address(self, safe_address: str) -> Optional[Dict[str, Any]]:
        """Get Safe by address"""
        try:
            result = self.client.table("safes").select("*").eq("safe_address", safe_address).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting Safe: {e}")
            return None
    
    async def get_safe_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Get Safe by Telegram ID"""
        try:
            result = self.client.table("safes").select("*").eq("telegram_id", telegram_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting Safe: {e}")
            return None
    
    async def create_transaction_record(
        self,
        safe_address: str,
        tx_hash: str,
        to_address: str,
        value: str,
        data: str,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a transaction record"""
        try:
            data_obj = {
                "safe_address": safe_address,
                "tx_hash": tx_hash,
                "to_address": to_address,
                "value": value,
                "data": data,
                "status": status
            }
            result = self.client.table("transactions").insert(data_obj).execute()
            logger.info(f"Created transaction record: {tx_hash}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise
    
    async def update_transaction_status(self, tx_hash: str, status: str) -> None:
        """Update transaction status"""
        try:
            self.client.table("transactions").update({"status": status}).eq("tx_hash", tx_hash).execute()
            logger.info(f"Updated transaction {tx_hash} status to {status}")
        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            raise


# Global database instance
db = Database()
