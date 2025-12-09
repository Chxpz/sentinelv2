from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from config import settings
from database import db
from safe_service import safe_service
import logging
from typing import Dict
import asyncio

logger = logging.getLogger(__name__)

# Store pending transactions for approval
pending_transactions: Dict[str, Dict] = {}


class TelegramBot:
    """Telegram bot for user interaction"""
    
    def __init__(self):
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("onboard", self.onboard_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        await update.message.reply_text(
            f"👋 Welcome to Treasury Sentinel, {user.first_name}!\n\n"
            "I'm your AI co-signer for Safe multisig wallets.\n\n"
            "Use /onboard to create a new 2-of-3 Safe wallet.\n"
            "Use /help to see all available commands."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 *Available Commands:*\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/onboard - Create a new Safe wallet (provide 2 owner addresses)\n"
            "/status - Check your Safe wallet status\n\n"
            "*How it works:*\n"
            "1. Create a 2-of-3 Safe with /onboard\n"
            "2. I'll detect pending transactions\n"
            "3. You approve/reject via Telegram\n"
            "4. I co-sign approved transactions\n"
            "5. Safe executes the transaction"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def onboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /onboard command"""
        user_id = str(update.effective_user.id)
        
        # Check if user already has a Safe
        existing_safe = await db.get_safe_by_telegram_id(user_id)
        if existing_safe:
            await update.message.reply_text(
                f"✅ You already have a Safe wallet!\n\n"
                f"Safe Address: `{existing_safe['safe_address']}`\n"
                f"Owner 1: `{existing_safe['owner1_address']}`\n"
                f"Owner 2: `{existing_safe['owner2_address']}`\n"
                f"Agent: `{existing_safe['agent_address']}`",
                parse_mode='Markdown'
            )
            return
        
        # Check if addresses were provided
        if len(context.args) != 2:
            await update.message.reply_text(
                "❌ Please provide 2 Ethereum addresses:\n"
                "`/onboard <owner1_address> <owner2_address>`\n\n"
                "Example:\n"
                "`/onboard 0x1234... 0x5678...`",
                parse_mode='Markdown'
            )
            return
        
        owner1_address = context.args[0]
        owner2_address = context.args[1]
        
        try:
            # Create the Safe
            safe_address, safe_info = safe_service.create_safe(owner1_address, owner2_address)
            
            # Store in database
            await db.create_safe(
                telegram_id=user_id,
                safe_address=safe_address,
                owner1_address=safe_info['owners'][0],
                owner2_address=safe_info['owners'][1],
                agent_address=safe_info['owners'][2]
            )
            
            await update.message.reply_text(
                f"🎉 *Safe Wallet Created Successfully!*\n\n"
                f"Safe Address: `{safe_address}`\n"
                f"Threshold: 2 of 3\n\n"
                f"*Owners:*\n"
                f"1. `{safe_info['owners'][0]}`\n"
                f"2. `{safe_info['owners'][1]}`\n"
                f"3. `{safe_info['owners'][2]}` (AI Agent)\n\n"
                f"I'll notify you when there are pending transactions!",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error creating Safe: {e}")
            await update.message.reply_text(
                f"❌ Error creating Safe: {str(e)}\n"
                "Please check the addresses and try again."
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = str(update.effective_user.id)
        
        safe = await db.get_safe_by_telegram_id(user_id)
        if not safe:
            await update.message.reply_text(
                "❌ You don't have a Safe wallet yet.\n"
                "Use /onboard to create one!"
            )
            return
        
        await update.message.reply_text(
            f"📊 *Your Safe Status*\n\n"
            f"Safe Address: `{safe['safe_address']}`\n"
            f"Status: {safe['status']}\n"
            f"Owner 1: `{safe['owner1_address']}`\n"
            f"Owner 2: `{safe['owner2_address']}`\n"
            f"Agent: `{safe['agent_address']}`",
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        await update.message.reply_text(
            "I don't understand that command. Use /help to see available commands."
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = str(update.effective_user.id)
        
        if data.startswith("approve_"):
            tx_id = data.replace("approve_", "")
            await self.approve_transaction(query, user_id, tx_id)
        elif data.startswith("reject_"):
            tx_id = data.replace("reject_", "")
            await self.reject_transaction(query, user_id, tx_id)
    
    async def approve_transaction(self, query, user_id: str, tx_id: str):
        """Handle transaction approval"""
        if tx_id not in pending_transactions:
            await query.edit_message_text("❌ Transaction not found or already processed.")
            return
        
        tx_data = pending_transactions[tx_id]
        
        try:
            # Sign the transaction with the agent's key
            signature = safe_service.sign_transaction(
                safe_address=tx_data['safe_address'],
                to=tx_data['to'],
                value=tx_data['value'],
                data=tx_data['data'],
                nonce=tx_data.get('nonce', 0)
            )
            
            # Update database
            await db.update_transaction_status(tx_id, "approved")
            
            # Remove from pending
            del pending_transactions[tx_id]
            
            await query.edit_message_text(
                f"✅ *Transaction Approved!*\n\n"
                f"Transaction ID: `{tx_id}`\n"
                f"Agent signature: `{signature[:20]}...`\n\n"
                f"The transaction has been co-signed by the AI agent.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error approving transaction: {e}")
            await query.edit_message_text(f"❌ Error approving transaction: {str(e)}")
    
    async def reject_transaction(self, query, user_id: str, tx_id: str):
        """Handle transaction rejection"""
        if tx_id not in pending_transactions:
            await query.edit_message_text("❌ Transaction not found or already processed.")
            return
        
        try:
            # Update database
            await db.update_transaction_status(tx_id, "rejected")
            
            # Remove from pending
            del pending_transactions[tx_id]
            
            await query.edit_message_text(
                f"❌ *Transaction Rejected*\n\n"
                f"Transaction ID: `{tx_id}`\n\n"
                f"The transaction will not be co-signed.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error rejecting transaction: {e}")
            await query.edit_message_text(f"❌ Error rejecting transaction: {str(e)}")
    
    async def notify_pending_transaction(
        self,
        telegram_id: str,
        tx_id: str,
        safe_address: str,
        to: str,
        value: int,
        data: str
    ):
        """Send notification about pending transaction"""
        try:
            # Store in pending transactions
            pending_transactions[tx_id] = {
                'safe_address': safe_address,
                'to': to,
                'value': value,
                'data': data,
                'telegram_id': telegram_id
            }
            
            # Create approval buttons
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{tx_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{tx_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Format message
            value_eth = value / 10**18
            message = (
                f"🔔 *New Pending Transaction*\n\n"
                f"Safe: `{safe_address}`\n"
                f"To: `{to}`\n"
                f"Value: {value_eth} ETH\n"
                f"Data: `{data[:20]}...`\n\n"
                f"Do you want to approve this transaction?"
            )
            
            # Send notification
            await self.app.bot.send_message(
                chat_id=telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Sent transaction notification to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def start_polling(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping Telegram bot...")
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()


# Global bot instance
telegram_bot = TelegramBot()
