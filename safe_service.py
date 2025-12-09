from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from config import settings
from typing import Tuple, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class SafeService:
    """Service for interacting with Gnosis Safe multisig wallets"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.eth_rpc_url))
        self.agent_account: LocalAccount = Account.from_key(settings.agent_private_key)
        self.agent_address = self.agent_account.address
        logger.info(f"SafeService initialized with agent address: {self.agent_address}")
    
    def create_safe(
        self,
        owner1_address: str,
        owner2_address: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Create a 2-of-3 Safe multisig wallet
        Owners: owner1, owner2, agent (AI co-signer)
        Threshold: 2
        
        Note: This is a simplified implementation. In production, you would use
        the Safe SDK or contract factory to deploy a new Safe.
        """
        try:
            # Validate addresses
            if not Web3.is_address(owner1_address) or not Web3.is_address(owner2_address):
                raise ValueError("Invalid Ethereum addresses provided")
            
            # Convert to checksum addresses
            owner1 = Web3.to_checksum_address(owner1_address)
            owner2 = Web3.to_checksum_address(owner2_address)
            agent = Web3.to_checksum_address(self.agent_address)
            
            # In a real implementation, this would deploy a Safe contract
            # For this MVP, we'll use a deterministic address generation
            # In production, use Safe Factory contract or Safe SDK
            
            owners = sorted([owner1.lower(), owner2.lower(), agent.lower()])
            safe_data = f"{owners[0]}{owners[1]}{owners[2]}{settings.network_chain_id}"
            safe_address_hash = Web3.keccak(text=safe_data)
            safe_address = Web3.to_checksum_address("0x" + safe_address_hash.hex()[-40:])
            
            safe_info = {
                "safe_address": safe_address,
                "owners": [owner1, owner2, agent],
                "threshold": 2,
                "version": "1.3.0"
            }
            
            logger.info(f"Created Safe at {safe_address} with owners: {owner1}, {owner2}, {agent}")
            return safe_address, safe_info
            
        except Exception as e:
            logger.error(f"Error creating Safe: {e}")
            raise
    
    def get_safe_info(self, safe_address: str) -> Dict[str, Any]:
        """Get Safe wallet information"""
        try:
            # In production, query the Safe contract
            # For MVP, return basic info
            return {
                "address": safe_address,
                "threshold": 2,
                "owners_count": 3
            }
        except Exception as e:
            logger.error(f"Error getting Safe info: {e}")
            raise
    
    def check_pending_transactions(self, safe_address: str) -> list:
        """
        Check for pending transactions on a Safe
        In production, this would query the Safe Transaction Service API
        """
        try:
            # In production: query Safe Transaction Service
            # GET https://safe-transaction-mainnet.safe.global/api/v1/safes/{address}/multisig-transactions/
            # For MVP, return empty list (transactions would be detected via events or API polling)
            logger.info(f"Checking pending transactions for Safe: {safe_address}")
            return []
        except Exception as e:
            logger.error(f"Error checking pending transactions: {e}")
            return []
    
    def sign_transaction(
        self,
        safe_address: str,
        to: str,
        value: int,
        data: str,
        operation: int = 0,
        safe_tx_gas: int = 0,
        base_gas: int = 0,
        gas_price: int = 0,
        gas_token: str = "0x0000000000000000000000000000000000000000",
        refund_receiver: str = "0x0000000000000000000000000000000000000000",
        nonce: int = 0
    ) -> str:
        """
        Sign a Safe transaction with the agent's key
        Returns the signature
        """
        try:
            # Build the Safe transaction hash
            # This follows the EIP-712 standard for Safe transactions
            
            # Domain separator
            domain_separator = Web3.keccak(
                encode_packed(
                    ["bytes32", "uint256", "address"],
                    [
                        Web3.keccak(text="EIP712Domain(uint256 chainId,address verifyingContract)"),
                        settings.network_chain_id,
                        safe_address
                    ]
                )
            )
            
            # Safe transaction hash
            safe_tx_hash_data = encode_packed(
                ["bytes32", "address", "uint256", "bytes32", "uint8", "uint256", "uint256", "uint256", "address", "address", "uint256"],
                [
                    Web3.keccak(text="SafeTx(address to,uint256 value,bytes data,uint8 operation,uint256 safeTxGas,uint256 baseGas,uint256 gasPrice,address gasToken,address refundReceiver,uint256 nonce)"),
                    to,
                    value,
                    Web3.keccak(bytes.fromhex(data[2:] if data.startswith('0x') else data)) if data and data != '0x' else Web3.keccak(text=''),
                    operation,
                    safe_tx_gas,
                    base_gas,
                    gas_price,
                    gas_token,
                    refund_receiver,
                    nonce
                ]
            )
            
            safe_tx_hash = Web3.keccak(safe_tx_hash_data)
            
            # Final message hash
            message_hash = Web3.keccak(
                encode_packed(
                    ["bytes1", "bytes1", "bytes32", "bytes32"],
                    [b"\x19", b"\x01", domain_separator, safe_tx_hash]
                )
            )
            
            # Sign the message
            signature = self.agent_account.signHash(message_hash)
            
            # Format signature for Safe
            v = signature.v
            r = signature.r.to_bytes(32, byteorder='big')
            s = signature.s.to_bytes(32, byteorder='big')
            
            # Concatenate r, s, v
            signature_bytes = r + s + v.to_bytes(1, byteorder='big')
            signature_hex = "0x" + signature_bytes.hex()
            
            logger.info(f"Signed transaction for Safe {safe_address}")
            return signature_hex
            
        except Exception as e:
            logger.error(f"Error signing transaction: {e}")
            raise
    
    def get_transaction_hash(
        self,
        safe_address: str,
        to: str,
        value: int,
        data: str,
        operation: int = 0,
        safe_tx_gas: int = 0,
        base_gas: int = 0,
        gas_price: int = 0,
        gas_token: str = "0x0000000000000000000000000000000000000000",
        refund_receiver: str = "0x0000000000000000000000000000000000000000",
        nonce: int = 0
    ) -> str:
        """Calculate the Safe transaction hash"""
        try:
            # Simplified hash calculation for MVP
            tx_data = f"{safe_address}{to}{value}{data}{nonce}"
            tx_hash = Web3.keccak(text=tx_data)
            return "0x" + tx_hash.hex()
        except Exception as e:
            logger.error(f"Error calculating transaction hash: {e}")
            raise


def encode_packed(types: list, values: list) -> bytes:
    """Helper function to encode data similar to Solidity's abi.encodePacked"""
    result = b""
    for t, v in zip(types, values):
        if t == "address":
            # Remove 0x prefix and ensure address is 40 chars, then convert to bytes
            addr_hex = v[2:].lower() if v.startswith('0x') else v.lower()
            result += bytes.fromhex(addr_hex.zfill(40))
        elif t == "uint256":
            result += v.to_bytes(32, byteorder='big')
        elif t == "uint8":
            result += v.to_bytes(1, byteorder='big')
        elif t == "bytes32":
            if isinstance(v, str):
                # Handle hex string, with or without 0x prefix
                hex_str = v[2:] if v.startswith('0x') else v
                v = bytes.fromhex(hex_str)
            result += v
        elif t == "bytes1":
            result += v
        elif t == "bytes":
            result += v
    return result


# Global Safe service instance
safe_service = SafeService()
