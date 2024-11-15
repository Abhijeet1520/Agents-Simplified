import os
import requests
from typing import Any, Dict, Optional
from web3 import Web3
from eth_account import Account

class OneInchClient:
    def __init__(self, private_key: Optional[str] = None, network_id: int = 1):
        """
        Initialize the OneInchClient.

        Args:
            private_key (Optional[str]): The private key of the wallet to sign transactions.
            network_id (int): The network ID (1 for Ethereum mainnet).
        """
        self.network_id = network_id
        self.base_url = f"https://fusion.1inch.io"
        self.api_version = "v1.0"
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))

        if private_key:
            self.account = Account.from_key(private_key)
            self.private_key = private_key
        else:
            # Generate a new account if no private key is provided
            self.account, self.private_key = Account.create_with_mnemonic()

    def swap_tokens(self, from_token: str, to_token: str, amount: int, recipient: Optional[str] = None, slippage: float = 1.0) -> Dict[str, Any]:
        """
        Swap tokens using the 1inch Fusion Plus API.

        Args:
            from_token (str): The address of the token to swap from.
            to_token (str): The address of the token to swap to.
            amount (int): The amount of from_token to swap (in its smallest unit).
            recipient (Optional[str]): The address to receive the tokens. Defaults to the client's address.
            slippage (float): The maximum acceptable slippage percentage.

        Returns:
            Dict[str, Any]: Transaction details or error information.
        """
        if not recipient:
            recipient = self.account.address

        # Prepare the request payload
        url = f"{self.base_url}/{self.api_version}/{self.network_id}/swap"
        params = {
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount),
            "fromAddress": self.account.address,
            "slippage": str(slippage),
            "destReceiver": recipient,
            "disableEstimate": "true"
        }

        # Fetch the swap data from the Fusion Plus API
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()

            # Extract transaction data
            tx_data = data.get("tx")
            if not tx_data:
                raise Exception("Transaction data not found in the response.")

            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return {"tx_hash": tx_hash.hex(), "transaction": tx_data}
        else:
            raise Exception(f"Swap failed: {response.status_code} {response.text}")

    def get_quote(self, from_token: str, to_token: str, amount: int) -> Dict[str, Any]:
        """
        Get a price quote for swapping tokens from the Fusion Plus API.

        Args:
            from_token (str): The address of the token to swap from.
            to_token (str): The address of the token to swap to.
            amount (int): The amount of from_token to swap (in its smallest unit).

        Returns:
            Dict[str, Any]: Quote details or error information.
        """
        url = f"{self.base_url}/{self.api_version}/{self.network_id}/quote"
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
        """
        Fetch active orders using the Fusion Plus API.

        Returns:
            Dict[str, Any]: Active orders or error information.
        """
        url = f"{self.base_url}/{self.api_version}/{self.network_id}/orders/address/{self.account.address}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch active orders: {response.status_code} {response.text}")

    def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order using the Fusion Plus API.

        Args:
            order_params (Dict[str, Any]): Parameters required to place an order.

        Returns:
            Dict[str, Any]: Order confirmation or error information.
        """
        url = f"{self.base_url}/{self.api_version}/{self.network_id}/orders"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=order_params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to place order: {response.status_code} {response.text}")

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an active order.

        Args:
            order_id (str): The ID of the order to cancel.

        Returns:
            Dict[str, Any]: Cancellation confirmation or error information.
        """
        url = f"{self.base_url}/{self.api_version}/{self.network_id}/orders/{order_id}/cancel"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to cancel order: {response.status_code} {response.text}")
