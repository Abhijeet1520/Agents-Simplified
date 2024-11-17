import os
import json
from typing import Any, Dict
from .client import OneInchClient  # Ensure correct import

client = OneInchClient()

def swap_tokens(from_token: str, to_token: str, amount: int, recipient: str, slippage: float = 100) -> Dict[str, Any]:
    """
    Swap tokens using OneInchClient.
    """
    try:
        result = client.swap_tokens(from_token, to_token, amount, recipient, slippage)
        return result if result else {}
    except Exception as e:
        print(f"Error in swap_tokens action: {e}")
        return {}

def get_quote(src_chain: int, dst_chain: int, from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
    """
    Fetch quote details from the OneInchClient.
    """
    try:
        quote = client.get_quote(
            src_chain=src_chain,
            dst_chain=dst_chain,
            from_token=from_token,
            to_token=to_token,
            amount=amount
        )
        return quote if quote else {}
    except Exception as e:
        print(f"Error in get_quote action: {e}")
        return {}

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders from the OneInchClient.
    """
    try:
        orders = client.fetch_active_orders()
        return orders if orders else {}
    except Exception as e:
        print(f"Error in fetch_active_orders action: {e}")
        return {}
