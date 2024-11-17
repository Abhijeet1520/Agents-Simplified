from typing import Any, Dict
from oneinch.client import OneInchClient

# Initialize OneInchClient
client = OneInchClient()

def swap_tokens(token_in_address: str, token_out_address: str, amount_in_wei: int, slippage: float = 100) -> Dict[str, Any]:
    """
    Execute a token swap using the 1inch Protocol.

    Args:
        token_in_address (str): The address of the token to swap from
        token_out_address (str): The address of the token to swap to
        amount_in_wei (int): The amount of input tokens in wei
        slippage (float, optional): Maximum acceptable slippage where 100 = 1%. Defaults to 100.

    Returns:
        Dict[str, Any]: The swap transaction result or empty dict if failed
    """
    try:
        result = client.swap_tokens(token_in_address, token_out_address, amount_in_wei, slippage)
        return result if result else {}
    except Exception as e:
        print(f"Error in swap_tokens: {e}")
        return {}

def fetch_quote(src_chain: int, dst_chain: int, from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
    """
    Fetch a quote for a token swap from 1inch.
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
        print(f"Error in fetch_quote: {e}")
        return {}

def fetch_active_orders() -> Dict[str, Any]:
    """
    Fetch active orders from 1inch Fusion Plus.

    Returns:
        Dict[str, Any]: Active orders information or empty dict if failed
    """
    try:
        orders = client.fetch_active_orders()
        return orders if orders else {}
    except Exception as e:
        print(f"Error in fetch_active_orders: {e}")
        return {}
