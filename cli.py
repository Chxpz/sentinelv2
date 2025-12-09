#!/usr/bin/env python3
"""
CLI interface for Treasury Sentinel
Allows users to onboard and manage Safe wallets via command line
"""
import asyncio
import argparse
import sys
from config import settings
from database import db
from safe_service import safe_service
from telegram_bot import telegram_bot


async def onboard(telegram_id: str, owner1: str, owner2: str):
    """Onboard a new user with a Safe wallet"""
    print(f"\n🔐 Creating 2-of-3 Safe Multisig Wallet...")
    print(f"Telegram ID: {telegram_id}")
    print(f"Owner 1: {owner1}")
    print(f"Owner 2: {owner2}")
    print(f"Agent: {safe_service.agent_address}")
    
    try:
        # Check if user already has a Safe
        existing_safe = await db.get_safe_by_telegram_id(telegram_id)
        if existing_safe:
            print(f"\n❌ Error: User already has a Safe at {existing_safe['safe_address']}")
            return
        
        # Create the Safe
        safe_address, safe_info = safe_service.create_safe(owner1, owner2)
        
        # Store in database
        result = await db.create_safe(
            telegram_id=telegram_id,
            safe_address=safe_address,
            owner1_address=safe_info['owners'][0],
            owner2_address=safe_info['owners'][1],
            agent_address=safe_info['owners'][2]
        )
        
        print(f"\n✅ Safe Created Successfully!")
        print(f"\nSafe Address: {safe_address}")
        print(f"Threshold: 2 of 3")
        print(f"\nOwners:")
        print(f"  1. {safe_info['owners'][0]}")
        print(f"  2. {safe_info['owners'][1]}")
        print(f"  3. {safe_info['owners'][2]} (AI Agent)")
        print(f"\n💡 The user can now interact via Telegram bot to approve transactions.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


async def status(telegram_id: str):
    """Check Safe status for a user"""
    print(f"\n🔍 Checking Safe status for Telegram ID: {telegram_id}")
    
    try:
        safe = await db.get_safe_by_telegram_id(telegram_id)
        if not safe:
            print(f"\n❌ No Safe found for this user.")
            print(f"Use 'onboard' command to create a new Safe.")
            return
        
        print(f"\n✅ Safe Found!")
        print(f"\nSafe Address: {safe['safe_address']}")
        print(f"Status: {safe['status']}")
        print(f"\nOwners:")
        print(f"  1. {safe['owner1_address']}")
        print(f"  2. {safe['owner2_address']}")
        print(f"  3. {safe['agent_address']} (AI Agent)")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


async def notify_transaction(safe_address: str, to: str, value: int, data: str = "0x"):
    """Manually trigger a transaction notification"""
    print(f"\n📤 Sending transaction notification...")
    print(f"Safe: {safe_address}")
    print(f"To: {to}")
    print(f"Value: {value} wei")
    
    try:
        # Get Safe info
        safe = await db.get_safe_by_address(safe_address)
        if not safe:
            print(f"\n❌ Safe not found: {safe_address}")
            return
        
        # Generate transaction hash
        tx_hash = safe_service.get_transaction_hash(
            safe_address=safe_address,
            to=to,
            value=value,
            data=data,
            nonce=0
        )
        
        # Create transaction record
        await db.create_transaction_record(
            safe_address=safe_address,
            tx_hash=tx_hash,
            to_address=to,
            value=str(value),
            data=data,
            status="pending"
        )
        
        # Send notification
        await telegram_bot.notify_pending_transaction(
            telegram_id=safe['telegram_id'],
            tx_id=tx_hash,
            safe_address=safe_address,
            to=to,
            value=value,
            data=data
        )
        
        print(f"\n✅ Notification sent!")
        print(f"Transaction Hash: {tx_hash}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Treasury Sentinel CLI - AI Co-Signer for Safe Multisig"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Onboard command
    onboard_parser = subparsers.add_parser('onboard', help='Onboard a new user with Safe wallet')
    onboard_parser.add_argument('telegram_id', help='Telegram user ID')
    onboard_parser.add_argument('owner1', help='First owner Ethereum address')
    onboard_parser.add_argument('owner2', help='Second owner Ethereum address')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check Safe status for a user')
    status_parser.add_argument('telegram_id', help='Telegram user ID')
    
    # Notify command (for testing)
    notify_parser = subparsers.add_parser('notify', help='Manually trigger transaction notification')
    notify_parser.add_argument('safe_address', help='Safe wallet address')
    notify_parser.add_argument('to', help='Destination address')
    notify_parser.add_argument('value', type=int, help='Value in wei')
    notify_parser.add_argument('--data', default='0x', help='Transaction data (default: 0x)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    if args.command == 'onboard':
        asyncio.run(onboard(args.telegram_id, args.owner1, args.owner2))
    elif args.command == 'status':
        asyncio.run(status(args.telegram_id))
    elif args.command == 'notify':
        asyncio.run(notify_transaction(args.safe_address, args.to, args.value, args.data))


if __name__ == '__main__':
    main()
