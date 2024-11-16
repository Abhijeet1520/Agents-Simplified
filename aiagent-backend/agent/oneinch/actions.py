import os
import time
from typing import Any, Dict, List
from .client import OneInchClient

client = OneInchClient(private_key=os.getenv("WALLET_PRIVATE_KEY"))

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

def approve_tokens(token_address: str, spender: str, amount: int) -> Dict[str, Any]:
    """
    Approve tokens for spending by the 1inch router.
    """
    return client.approve_tokens(token_address, spender, amount)

def place_fusion_plus_order(
    src_chain_id: int,
    dst_chain_id: int,
    src_token_address: str,
    dst_token_address: str,
    amount: str,
    wallet_address: str,
    invert: bool = False
) -> Dict[str, Any]:
    """
    Place a Fusion+ cross-chain order.
    """
    if invert:
        src_chain_id, dst_chain_id = dst_chain_id, src_chain_id
        src_token_address, dst_token_address = dst_token_address, src_token_address

    params = {
        "srcChainId": src_chain_id,
        "dstChainId": dst_chain_id,
        "srcTokenAddress": src_token_address,
        "dstTokenAddress": dst_token_address,
        "amount": amount,
        "enableEstimate": True,
        "walletAddress": wallet_address
    }

    # Get a quote
    quote = client.get_quote(**params)
    print("Received Fusion+ quote from 1inch API")

    # Generate secrets and secret hashes
    secrets_count = quote.get_preset().secretsCount
    secrets = [client.get_random_bytes32() for _ in range(secrets_count)]
    secret_hashes = [client.hash_secret(s) for s in secrets]

    if secrets_count == 1:
        hash_lock = client.hash_lock_single(secrets[0])
    else:
        hash_lock = client.hash_lock_multiple(secret_hashes)

    # Place the order
    order_response = client.place_order(
        quote=quote,
        wallet_address=wallet_address,
        hash_lock=hash_lock,
        secret_hashes=secret_hashes
    )
    print("Order successfully placed")

    # Monitor the order
    order_hash = order_response['orderHash']
    monitor_order(order_hash, secrets)

    return order_response

def monitor_order(order_hash: str, secrets: List[str]):
    """
    Monitor the order status and submit secrets when fills are ready.
    """
    while True:
        print("Polling for fills until order status is set to 'executed'...")
        try:
            order = client.get_order_status(order_hash)
            if order['status'] == 'executed':
                print("Order is complete. Exiting.")
                break

            fills_object = client.get_ready_to_accept_secret_fills(order_hash)
            if fills_object.get('fills'):
                for fill in fills_object['fills']:
                    idx = fill['idx']
                    client.submit_secret(order_hash, secrets[idx])
                    print(f"Secret submitted for fill index {idx}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)
