from web3 import Web3
from typing import Any, Dict
import os
import json
import time
import requests
from oneinch import OneInchClient

client = OneInchClient()

def swap_tokens(token_in_address: str, token_out_address: str, amount_in_wei: int, slippage: float) -> Dict[str, Any]:
    """
    Swap tokens using OneInchClient.
    """
    result = client.swap_tokens(token_in_address, token_out_address, amount_in_wei, slippage)
    return result

def fetch_quote(from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
    """
    Fetch quote details from the OneInchClient.
    """
    quote = client.get_quote(from_token, to_token, amount)
    return quote

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders from the OneInchClient.
    """
    orders = client.fetch_active_orders()
    return orders
