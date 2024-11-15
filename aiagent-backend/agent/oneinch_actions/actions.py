from typing import Any, Dict
from .client import OneInchClient

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
    Fetch active orders using OneInchClient.
    """
    return client.fetch_active_orders()
