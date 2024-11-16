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
    return client.swap_tokens(token_in_address, token_out_address, amount_in_wei, slippage)

def fetch_quote() -> Dict[str, Any]:
    """
    Fetch quote details from the OneInchClient.
    """
    params = {
        "srcChain": "1",
        "dstChain": "137",
        "srcTokenAddress": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "dstTokenAddress": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",
        "amount": "100000000000000000",
        "walletAddress": client.account.address,
        "enableEstimate": "true",
        "fee": "0"
    }
    return client.get_quote(params)

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders from the 1inch API.

    Returns:
        Dict[str, Any]: Active orders data.
    """
    api_url = "https://api.1inch.dev/fusion-plus/orders/v1.0/order/active"
    api_key = os.getenv('ONEINCH_API_KEY')
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch active orders: {response.status_code} {response.text}")
