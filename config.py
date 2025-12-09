from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Telegram
    telegram_bot_token: str
    
    # Ethereum
    eth_rpc_url: str
    network_chain_id: int = 1
    
    # Agent wallet
    agent_private_key: str
    
    # Safe configuration
    safe_factory_address: Optional[str] = None
    safe_master_copy_address: Optional[str] = None
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
