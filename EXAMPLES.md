# Treasury Sentinel - Example Usage Guide

This guide demonstrates how to use the Treasury Sentinel MVP with example commands and flows.

## Prerequisites Setup

Before running the examples, ensure you have:

1. **Installed dependencies**:
```bash
pip install -r requirements.txt
```

2. **Created and configured .env file**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Set up Supabase database**:
- Run the SQL from `schema.sql` in your Supabase SQL Editor

## Example 1: Onboarding via CLI

Create a Safe wallet for a user:

```bash
# Replace with actual values
python cli.py onboard 123456789 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
```

Expected output:
```
🔐 Creating 2-of-3 Safe Multisig Wallet...
Telegram ID: 123456789
Owner 1: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
Owner 2: 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
Agent: 0x...

✅ Safe Created Successfully!

Safe Address: 0x...
Threshold: 2 of 3

Owners:
  1. 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
  2. 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
  3. 0x... (AI Agent)

💡 The user can now interact via Telegram bot to approve transactions.
```

## Example 2: Check Status via CLI

Check the status of a user's Safe:

```bash
python cli.py status 123456789
```

Expected output:
```
🔍 Checking Safe status for Telegram ID: 123456789

✅ Safe Found!

Safe Address: 0x...
Status: active

Owners:
  1. 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
  2. 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
  3. 0x... (AI Agent)
```

## Example 3: Telegram Bot Onboarding

1. Start your bot:
```bash
python main.py
```

2. On Telegram, message your bot:
```
/start
```

Expected response:
```
👋 Welcome to Treasury Sentinel!

I'm your AI co-signer for Safe multisig wallets.

Use /onboard to create a new 2-of-3 Safe wallet.
Use /help to see all available commands.
```

3. Create a Safe:
```
/onboard 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
```

Expected response:
```
🎉 Safe Wallet Created Successfully!

Safe Address: 0x...
Threshold: 2 of 3

Owners:
1. 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
2. 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
3. 0x... (AI Agent)

I'll notify you when there are pending transactions!
```

## Example 4: Transaction Approval Flow

### Trigger a notification (for testing):

```bash
python cli.py notify 0xYOUR_SAFE_ADDRESS 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0 1000000000000000000
```

### On Telegram, you'll receive:

```
🔔 New Pending Transaction

Safe: 0x...
To: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
Value: 1.0 ETH
Data: 0x...

Do you want to approve this transaction?
[✅ Approve] [❌ Reject]
```

### Click "✅ Approve":

```
✅ Transaction Approved!

Transaction ID: 0x...
Agent signature: 0x...

The transaction has been co-signed by the AI agent.
```

### Click "❌ Reject":

```
❌ Transaction Rejected

Transaction ID: 0x...

The transaction will not be co-signed.
```

## Example 5: Using the REST API

Start the API server:
```bash
python main.py
```

### Create a Safe via API:

```bash
curl -X POST http://localhost:8000/api/safe/create \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": "987654321",
    "owner1_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    "owner2_address": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
  }'
```

Expected response:
```json
{
  "safe_address": "0x...",
  "owner1_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  "owner2_address": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
  "agent_address": "0x...",
  "status": "active"
}
```

### Get Safe info:

```bash
curl http://localhost:8000/api/safe/0xYOUR_SAFE_ADDRESS
```

Expected response:
```json
{
  "id": 1,
  "telegram_id": "987654321",
  "safe_address": "0x...",
  "owner1_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  "owner2_address": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
  "agent_address": "0x...",
  "status": "active",
  "created_at": "2025-12-09T04:00:00.000Z"
}
```

### Notify pending transaction:

```bash
curl -X POST http://localhost:8000/api/transaction/notify \
  -H "Content-Type: application/json" \
  -d '{
    "safe_address": "0xYOUR_SAFE_ADDRESS",
    "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    "value": 1000000000000000000,
    "data": "0x",
    "nonce": 0
  }'
```

Expected response:
```json
{
  "status": "ok",
  "tx_hash": "0x...",
  "message": "Notification sent to user"
}
```

## Example 6: Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Complete End-to-End Flow Example

1. **Setup** (one-time):
   - Configure .env with credentials
   - Set up Supabase database
   - Create Telegram bot

2. **Start the application**:
   ```bash
   python main.py
   ```

3. **User onboards via Telegram**:
   - User: `/onboard 0xOwner1... 0xOwner2...`
   - Bot creates 2-of-3 Safe and stores in database

4. **Transaction is initiated** (on-chain or simulated):
   - External system detects pending Safe transaction
   - System calls: `POST /api/transaction/notify`

5. **User receives Telegram notification**:
   - Bot sends message with transaction details
   - Shows [Approve] [Reject] buttons

6. **User approves**:
   - User clicks "Approve"
   - Agent signs transaction with its private key
   - Signature is returned to user

7. **Transaction executes**:
   - With 2 signatures (user + agent), threshold is met
   - Transaction can be executed on Safe contract

## Testing Checklist

- [ ] Dependencies install correctly
- [ ] .env file is configured
- [ ] Database schema is created in Supabase
- [ ] Telegram bot responds to /start
- [ ] CLI onboard command works
- [ ] Telegram /onboard command works
- [ ] Safe creation stores data in database
- [ ] Transaction notification sends to Telegram
- [ ] Approve button generates valid signature
- [ ] Reject button updates transaction status
- [ ] API endpoints return expected responses
- [ ] Docker container builds and runs

## Common Issues and Solutions

### Issue: "Module not found" errors
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Issue: "Settings validation error"
**Solution**: Ensure .env file exists and has all required values

### Issue: Telegram bot not responding
**Solution**: Check TELEGRAM_BOT_TOKEN is correct and bot is started

### Issue: Database errors
**Solution**: Verify Supabase credentials and schema is created

### Issue: "Invalid Ethereum address"
**Solution**: Ensure addresses start with 0x and are 42 characters

## Notes

- This is an MVP/prototype - NOT production ready
- Safe addresses are generated deterministically (simplified for MVP)
- In production, use actual Safe Factory contract deployment
- Agent private key should be secured properly (not in .env)
- Add proper authentication before production use
- Implement rate limiting and input validation
- Add comprehensive error handling and logging
