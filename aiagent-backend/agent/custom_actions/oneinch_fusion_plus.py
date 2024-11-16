from typing import Any, Dict
from oneinch import OneInchClient
import os
import json

# Initialize OneInchClient
client = OneInchClient()

def swap_tokens(token_in_address: str, token_out_address: str, amount_in_wei: int, slippage: float) -> Dict[str, Any]:
    """
    Swap tokens using OneInchClient.
    """
    try:
        result = client.swap_tokens(token_in_address, token_out_address, amount_in_wei, slippage)
        return result if result else {}
    except Exception as e:
        print(f"Error in swap_tokens: {e}")
        return {}

def fetch_quote(from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
    """
    Fetch quote details from the OneInchClient.
    """
    try:
        params = {
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount
        }
        quote = client.get_quote(params)
        return quote if quote else {}
    except Exception as e:
        print(f"Error in fetch_quote: {e}")
        return {}

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders from the OneInchClient.
    """
    try:
        orders = client.fetch_active_orders()
        return orders if orders else {}
    except Exception as e:
        print(f"Error in fetch_active_orders: {e}")
        return {}
