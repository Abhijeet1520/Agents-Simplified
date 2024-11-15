import os
import requests
from typing import Any, Dict
from web3 import Web3

class OneInchClient:
    def __init__(self):
        ...

    def swap_tokens(self, from_token: str, to_token: str, amount: int, recipient: str, slippage: float = 1.0) -> Dict[str, Any]:
        """
        Swap tokens using the 1inch Swap API.
        """
        url = f"https://api.1inch.io/v5.0/1/swap"
        params = {
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount),
            "fromAddress": self.account.address,
            "slippage": str(slippage),
            "destReceiver": recipient,
            "disableEstimate": "true"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            tx_data = response.json()["tx"]
            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return {"tx_hash": tx_hash.hex()}
        else:
            raise Exception(f"Swap failed: {response.status_code} {response.text}")

    def get_quote(self, from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
        """
        Get a price quote for swapping tokens from 1inch API.
        """
        url = f"https://api.1inch.io/v5.0/1/quote"
        params = {
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount)
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch quote: {response.status_code} {response.text}")

    def fetch_active_orders(self) -> Dict[str, Any]:
        # ...existing code...
        pass  # Rest of the fetch_active_orders method
