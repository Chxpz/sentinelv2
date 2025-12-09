from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from database import db
from safe_service import safe_service
from telegram_bot import telegram_bot
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Treasury Sentinel API", version="1.0.0")


class CreateSafeRequest(BaseModel):
    telegram_id: str
    owner1_address: str
    owner2_address: str


class PendingTransactionRequest(BaseModel):
    safe_address: str
    to: str
    value: int
    data: str = "0x"
    nonce: int = 0


class SafeInfoResponse(BaseModel):
    safe_address: str
    owner1_address: str
    owner2_address: str
    agent_address: str
    status: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Treasury Sentinel",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/safe/create", response_model=SafeInfoResponse)
async def create_safe(request: CreateSafeRequest):
    """
    Create a new 2-of-3 Safe multisig wallet
    """
    try:
        # Check if user already has a Safe
        existing_safe = await db.get_safe_by_telegram_id(request.telegram_id)
        if existing_safe:
            raise HTTPException(status_code=400, detail="User already has a Safe")
        
        # Create the Safe
        safe_address, safe_info = safe_service.create_safe(
            request.owner1_address,
            request.owner2_address
        )
        
        # Store in database
        result = await db.create_safe(
            telegram_id=request.telegram_id,
            safe_address=safe_address,
            owner1_address=safe_info['owners'][0],
            owner2_address=safe_info['owners'][1],
            agent_address=safe_info['owners'][2]
        )
        
        return SafeInfoResponse(
            safe_address=result['safe_address'],
            owner1_address=result['owner1_address'],
            owner2_address=result['owner2_address'],
            agent_address=result['agent_address'],
            status=result['status']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Safe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/safe/{safe_address}")
async def get_safe(safe_address: str):
    """
    Get Safe information by address
    """
    try:
        safe = await db.get_safe_by_address(safe_address)
        if not safe:
            raise HTTPException(status_code=404, detail="Safe not found")
        
        return safe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Safe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transaction/notify")
async def notify_pending_transaction(
    request: PendingTransactionRequest,
    background_tasks: BackgroundTasks
):
    """
    Notify user about a pending transaction
    This endpoint would typically be called by a monitoring service
    """
    try:
        # Get Safe info
        safe = await db.get_safe_by_address(request.safe_address)
        if not safe:
            raise HTTPException(status_code=404, detail="Safe not found")
        
        # Generate transaction hash
        tx_hash = safe_service.get_transaction_hash(
            safe_address=request.safe_address,
            to=request.to,
            value=request.value,
            data=request.data,
            nonce=request.nonce
        )
        
        # Create transaction record
        await db.create_transaction_record(
            safe_address=request.safe_address,
            tx_hash=tx_hash,
            to_address=request.to,
            value=str(request.value),
            data=request.data,
            status="pending"
        )
        
        # Send Telegram notification
        background_tasks.add_task(
            telegram_bot.notify_pending_transaction,
            telegram_id=safe['telegram_id'],
            tx_id=tx_hash,
            safe_address=request.safe_address,
            to=request.to,
            value=request.value,
            data=request.data
        )
        
        return {
            "status": "ok",
            "tx_hash": tx_hash,
            "message": "Notification sent to user"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error notifying transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transaction/sign")
async def sign_transaction(request: PendingTransactionRequest):
    """
    Sign a transaction with the agent's key
    (This is called internally after user approval)
    """
    try:
        # Get Safe info
        safe = await db.get_safe_by_address(request.safe_address)
        if not safe:
            raise HTTPException(status_code=404, detail="Safe not found")
        
        # Sign the transaction
        signature = safe_service.sign_transaction(
            safe_address=request.safe_address,
            to=request.to,
            value=request.value,
            data=request.data,
            nonce=request.nonce
        )
        
        return {
            "status": "ok",
            "signature": signature
        }
        
    except Exception as e:
        logger.error(f"Error signing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
