from typing import Any, Dict
from .client import OneInchClient

client = OneInchClient()

def swap_tokens(from_token: str, to_token: str, amount: int, recipient: str, slippage: float = 1.0) -> Dict[str, Any]:
    """
    Swap tokens using OneInchClient.
    """
    return client.swap_tokens(from_token, to_token, amount, recipient, slippage)

def get_quote(from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
    """
    Fetch quote details from the OneInchClient.
    """
    return client.get_quote(from_token, to_token, amount)

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders using OneInchClient.
    """
    return client.fetch_active_orders()
