#!/usr/bin/env python3
"""
Main entry point for Treasury Sentinel
Starts both the FastAPI server and Telegram bot
"""
import asyncio
import logging
import uvicorn
from api import app
from telegram_bot import telegram_bot
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def start_services():
    """Start all services"""
    logger.info("Starting Treasury Sentinel services...")
    
    # Start Telegram bot
    await telegram_bot.start_polling()
    logger.info("✅ Telegram bot started")
    
    # Note: FastAPI will be started by uvicorn in the main thread
    logger.info("✅ Services initialized")


async def stop_services():
    """Stop all services"""
    logger.info("Stopping Treasury Sentinel services...")
    await telegram_bot.stop()
    logger.info("✅ Services stopped")


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Treasury Sentinel - AI Co-Signer for Safe Multisig")
    logger.info("=" * 60)
    
    # Start Telegram bot in background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_services())
    
    # Start FastAPI server
    try:
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="info",
            loop="asyncio"
        )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        loop.run_until_complete(stop_services())
        loop.close()


if __name__ == "__main__":
    main()
