# Treasury Sentinel - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TREASURY SENTINEL MVP                                 │
│                      AI Co-Signer for Safe Multisig                          │
└─────────────────────────────────────────────────────────────────────────────┘

                          USER INTERACTION LAYER
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ┌──────────────────┐              ┌──────────────────┐                     │
│  │  Telegram Bot    │              │   CLI Interface  │                     │
│  │  (/start, /help) │              │  (onboard,       │                     │
│  │  (/onboard)      │              │   status, notify)│                     │
│  │  (/status)       │              │                  │                     │
│  │  [Approve/Reject]│              │                  │                     │
│  └────────┬─────────┘              └────────┬─────────┘                     │
│           │                                 │                               │
└───────────┼─────────────────────────────────┼───────────────────────────────┘
            │                                 │
            │                                 │
            ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         main.py (FastAPI + Bot)                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ api.py       │  │telegram_bot  │  │  cli.py      │  │ monitor.py   │   │
│  │              │  │    .py       │  │              │  │ (placeholder)│   │
│  │ REST API     │  │ Bot Handlers │  │ CLI Commands │  │ TX Monitor   │   │
│  │ Endpoints:   │  │              │  │              │  │              │   │
│  │ - /health    │  │ Commands:    │  │ Commands:    │  │ - Polling    │   │
│  │ - /safe/*    │  │ - /start     │  │ - onboard    │  │ - Webhooks   │   │
│  │ - /tx/*      │  │ - /onboard   │  │ - status     │  │ - Notify     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │            │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                         │
│                                                                               │
│  ┌──────────────────────┐              ┌──────────────────────┐             │
│  │   safe_service.py    │              │    database.py       │             │
│  │                      │              │                      │             │
│  │  - create_safe()     │              │  - create_safe()     │             │
│  │  - sign_transaction()│              │  - get_safe()        │             │
│  │  - check_pending()   │              │  - create_tx()       │             │
│  │  - get_tx_hash()     │              │  - update_tx()       │             │
│  │                      │              │                      │             │
│  │  Uses: Web3.py       │              │  Uses: Supabase SDK  │             │
│  │        eth-account   │              │                      │             │
│  └──────────┬───────────┘              └──────────┬───────────┘             │
│             │                                     │                         │
└─────────────┼─────────────────────────────────────┼─────────────────────────┘
              │                                     │
              ▼                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                                        │
│                                                                               │
│  ┌────────────────┐    ┌─────────────────┐    ┌────────────────┐           │
│  │  Ethereum RPC  │    │    Supabase     │    │   Telegram     │           │
│  │   (Alchemy/    │    │                 │    │   Bot API      │           │
│  │    Infura)     │    │  ┌───────────┐  │    │                │           │
│  │                │    │  │   safes   │  │    │  - Messages    │           │
│  │  - Web3 calls  │    │  └───────────┘  │    │  - Buttons     │           │
│  │  - Sign txs    │    │  ┌───────────┐  │    │  - Callbacks   │           │
│  │  - Query Safe  │    │  │transactions│ │    │                │           │
│  │                │    │  └───────────┘  │    │                │           │
│  └────────────────┘    └─────────────────┘    └────────────────┘           │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                          DATA FLOW DIAGRAM
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│   1. ONBOARDING FLOW:                                                        │
│      User ──/onboard owner1 owner2──▶ Telegram Bot                          │
│                                            │                                  │
│                                            ▼                                  │
│                                    safe_service.create_safe()                │
│                                            │                                  │
│                                            ▼                                  │
│                                    database.create_safe()                    │
│                                            │                                  │
│                                            ▼                                  │
│                                    Supabase (stores data)                    │
│                                            │                                  │
│                                            ▼                                  │
│      User ◀────Success message──────  Telegram Bot                          │
│                                                                               │
│   2. TRANSACTION APPROVAL FLOW:                                              │
│      External ──New pending TX──▶ POST /api/transaction/notify              │
│                                            │                                  │
│                                            ▼                                  │
│                                    database.create_transaction_record()      │
│                                            │                                  │
│                                            ▼                                  │
│                                    telegram_bot.notify_pending_transaction() │
│                                            │                                  │
│                                            ▼                                  │
│      User ◀────Notification message───  Telegram Bot                        │
│            with [Approve] [Reject] buttons                                   │
│                                                                               │
│      User ──clicks [Approve]──▶ Telegram Bot                                │
│                                            │                                  │
│                                            ▼                                  │
│                                    safe_service.sign_transaction()           │
│                                            │                                  │
│                                            ▼                                  │
│                                    Agent signs with private key              │
│                                            │                                  │
│                                            ▼                                  │
│                                    database.update_transaction_status()      │
│                                            │                                  │
│                                            ▼                                  │
│      User ◀────Signature & confirmation──  Telegram Bot                     │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                       COMPONENT DETAILS
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  config.py          - Settings management (env vars, Pydantic)              │
│  main.py            - Application startup (FastAPI + Telegram bot)          │
│  api.py             - REST API endpoints (5 endpoints)                       │
│  telegram_bot.py    - Bot commands and callback handlers                    │
│  cli.py             - CLI interface (3 commands)                             │
│  safe_service.py    - Safe operations (Web3.py integration)                 │
│  database.py        - Database operations (Supabase client)                 │
│  monitor.py         - Transaction monitoring (placeholder)                  │
│  setup_verify.py    - Setup verification script                             │
│                                                                               │
│  schema.sql         - Database schema (2 tables, indexes, RLS)              │
│  requirements.txt   - Python dependencies (10 packages)                     │
│  Dockerfile         - Container definition                                   │
│  docker-compose.yml - Service orchestration                                 │
│                                                                               │
│  README.md          - Comprehensive documentation                            │
│  EXAMPLES.md        - Usage examples and expected outputs                   │
│  IMPLEMENTATION_SUMMARY.md - Implementation details                         │
│  LICENSE            - MIT License                                            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                         DEPLOYMENT OPTIONS
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  Option 1: Docker Compose (Recommended)                                     │
│  ┌─────────────────────────────────────┐                                    │
│  │  $ docker-compose up -d             │                                    │
│  │  ✅ Containerized                    │                                    │
│  │  ✅ Easy deployment                  │                                    │
│  │  ✅ Environment isolation            │                                    │
│  └─────────────────────────────────────┘                                    │
│                                                                               │
│  Option 2: Local Development                                                │
│  ┌─────────────────────────────────────┐                                    │
│  │  $ python -m venv venv              │                                    │
│  │  $ source venv/bin/activate         │                                    │
│  │  $ pip install -r requirements.txt  │                                    │
│  │  $ python main.py                   │                                    │
│  │  ✅ Direct execution                 │                                    │
│  │  ✅ Easy debugging                   │                                    │
│  └─────────────────────────────────────┘                                    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                          KEY METRICS
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  📊 Code Statistics:                                                         │
│     • Total Lines of Code: ~2,380 lines                                     │
│     • Python Modules: 9 files                                               │
│     • Documentation: 4 files                                                │
│     • Configuration: 6 files                                                │
│                                                                               │
│  🔌 API Endpoints: 5 REST endpoints                                         │
│  💬 Telegram Commands: 4 user commands                                      │
│  🖥️  CLI Commands: 3 management commands                                     │
│  🗄️  Database Tables: 2 tables with indexes                                 │
│  📦 Dependencies: 10 Python packages                                        │
│                                                                               │
│  🔒 Security:                                                                │
│     • CodeQL Scan: ✅ 0 alerts                                               │
│     • Code Review: ✅ All issues fixed                                       │
│     • Input Validation: ⚠️ Basic (needs enhancement for production)         │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```
