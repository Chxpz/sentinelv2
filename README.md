# Treasury Sentinel v2 - AI Co-Signer for Safe Multisig

A minimal end-to-end prototype for an AI co-signer system that manages 2-of-3 Gnosis Safe multisig wallets via Telegram.

## 🌟 Features

- **2-of-3 Safe Multisig**: Create Safe wallets with two user-controlled owners and one AI agent
- **Telegram Integration**: Complete user onboarding and transaction approval via Telegram bot
- **CLI Support**: Alternative command-line interface for user management
- **Transaction Flow**: Detect pending transactions → Telegram notification → User approval → AI co-signs → Safe executes
- **Database Storage**: All Safe and transaction data stored in Supabase

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   User      │────▶│  Telegram    │────▶│   FastAPI   │
│ (Telegram)  │◀────│    Bot       │◀────│   Backend   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                  │
                                                  ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   Supabase   │◀────│    Web3     │
                    │   Database   │     │   Service   │
                    └──────────────┘     └─────────────┘
                                                  │
                                                  ▼
                                          ┌─────────────┐
                                          │   Gnosis    │
                                          │    Safe     │
                                          └─────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Supabase account and project
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Ethereum RPC endpoint (Alchemy, Infura, etc.)
- Private key for the AI agent wallet

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Chxpz/sentinelv2.git
cd sentinelv2
```

### 2. Set Up Supabase Database

1. Create a new project in [Supabase](https://supabase.com)
2. Go to the SQL Editor
3. Run the SQL script from `schema.sql`
4. Copy your project URL and anon key

### 3. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Ethereum Configuration
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-api-key
NETWORK_CHAIN_ID=1

# Agent Wallet (Private Key for AI co-signer)
AGENT_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
```

### 5. Run with Docker (Recommended)

```bash
docker-compose up -d
```

### 6. Or Run Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`

## 📱 Using the Telegram Bot

### Onboarding Flow

1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. Send `/onboard <owner1_address> <owner2_address>` with two Ethereum addresses

Example:
```
/onboard 0x1234567890123456789012345678901234567890 0xabcdefabcdefabcdefabcdefabcdefabcdefabcd
```

4. The bot will create a 2-of-3 Safe with:
   - Owner 1: Your first address
   - Owner 2: Your second address  
   - Owner 3: AI Agent (co-signer)

### Transaction Approval Flow

1. When a pending transaction is detected, you'll receive a Telegram message
2. Review the transaction details (Safe, destination, value)
3. Click "✅ Approve" or "❌ Reject"
4. If approved, the AI agent will co-sign the transaction
5. The transaction can then be executed on the Safe

### Available Commands

- `/start` - Welcome message and introduction
- `/help` - Show all available commands
- `/onboard <owner1> <owner2>` - Create a new Safe wallet
- `/status` - Check your Safe wallet status

## 💻 Using the CLI

The CLI provides an alternative to the Telegram bot for testing and management.

### Onboard a User

```bash
python cli.py onboard <telegram_id> <owner1_address> <owner2_address>
```

Example:
```bash
python cli.py onboard 123456789 0x1234...5678 0xabcd...efgh
```

### Check Status

```bash
python cli.py status <telegram_id>
```

### Manually Trigger Transaction Notification (Testing)

```bash
python cli.py notify <safe_address> <to_address> <value_in_wei>
```

Example:
```bash
python cli.py notify 0x9876...5432 0x1111...2222 1000000000000000000
```

## 🔌 API Endpoints

### Health Check
```
GET /
GET /health
```

### Create Safe
```
POST /api/safe/create
{
  "telegram_id": "123456789",
  "owner1_address": "0x...",
  "owner2_address": "0x..."
}
```

### Get Safe Info
```
GET /api/safe/{safe_address}
```

### Notify Pending Transaction
```
POST /api/transaction/notify
{
  "safe_address": "0x...",
  "to": "0x...",
  "value": 1000000000000000000,
  "data": "0x",
  "nonce": 0
}
```

### Sign Transaction
```
POST /api/transaction/sign
{
  "safe_address": "0x...",
  "to": "0x...",
  "value": 1000000000000000000,
  "data": "0x",
  "nonce": 0
}
```

## 📁 Project Structure

```
sentinelv2/
├── main.py              # Main entry point (FastAPI + Telegram bot)
├── api.py               # FastAPI REST API endpoints
├── telegram_bot.py      # Telegram bot handlers and logic
├── cli.py               # Command-line interface
├── safe_service.py      # Safe multisig wallet operations
├── database.py          # Supabase database interface
├── config.py            # Configuration and settings
├── schema.sql           # Database schema for Supabase
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose setup
├── .env.example         # Example environment variables
└── README.md            # This file
```

## 🔒 Security Notes

**⚠️ This is an MVP/Prototype - NOT production ready!**

For production use, you should:

1. **Implement proper authentication**: Add user authentication and authorization
2. **Secure the agent private key**: Use a proper key management solution (AWS KMS, HashiCorp Vault, etc.)
3. **Add rate limiting**: Prevent abuse of API endpoints
4. **Implement proper Safe deployment**: Use the actual Safe Factory contract instead of simulated addresses
5. **Add transaction validation**: Verify transaction details and implement spending limits
6. **Enable RLS policies**: Properly configure Row Level Security in Supabase
7. **Add monitoring**: Implement proper logging, monitoring, and alerting
8. **Use HTTPS**: Enable TLS/SSL for all API communications
9. **Add tests**: Comprehensive unit and integration tests
10. **Audit the code**: Get a professional security audit before production use

## 🛠️ Development

### Running Tests

```bash
# Coming soon - no tests in MVP
pytest
```

### Linting

```bash
# Format code
black .

# Check types
mypy .
```

## 📝 Database Schema

The application uses two main tables:

### `safes` Table
- `id`: Primary key
- `telegram_id`: Telegram user ID (unique)
- `safe_address`: Safe wallet address (unique)
- `owner1_address`: First owner address
- `owner2_address`: Second owner address
- `agent_address`: AI agent address
- `status`: Safe status (active/inactive)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### `transactions` Table
- `id`: Primary key
- `safe_address`: Associated Safe address
- `tx_hash`: Transaction hash (unique)
- `to_address`: Destination address
- `value`: Transaction value
- `data`: Transaction data
- `status`: Transaction status (pending/approved/rejected/executed)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## 🤝 Contributing

This is an MVP prototype. Contributions are welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [Gnosis Safe](https://safe.global/) - Smart contract wallet
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [Supabase](https://supabase.com/) - Backend as a Service
- [Web3.py](https://web3py.readthedocs.io/) - Ethereum Python library

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for secure multisig management**