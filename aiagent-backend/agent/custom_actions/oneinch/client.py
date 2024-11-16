import os
import requests
from typing import Any, Dict, List, Optional
from web3 import Web3
from eth_account import Account

class OneInchClient:
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize the OneInchClient.

        Args:
            private_key (Optional[str]): The private key of the wallet to sign transactions.
        """
        self.base_url = "https://api.1inch.dev"
        self.api_version = "v1.0"
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))

        # Retrieve the 1inch API key from the environment variable
        self.api_key = os.getenv("ONEINCH_API_KEY")
        if not self.api_key:
            raise ValueError("ONEINCH_API_KEY environment variable not set.")

        if private_key:
            self.account = Account.from_key(private_key)
            self.private_key = private_key
        else:
            # Generate a new account if no private key is provided
            self.account = Account.create()
            self.private_key = self.account.key

    def _get_headers(self) -> Dict[str, str]:
        """
        Internal method to get the headers for API requests, including the API key.

        Returns:
            Dict[str, str]: Headers dictionary.
        """
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_active_orders(
        self,
        page: int = 1,
        limit: int = 100,
        src_chain: Optional[int] = None,
        dst_chain: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get cross-chain swap active orders.

        Args:
            page (int): Pagination step, default is 1.
            limit (int): Number of active orders to receive (default: 100, max: 500).
            src_chain (Optional[int]): Source chain ID of cross-chain swaps.
            dst_chain (Optional[int]): Destination chain ID of cross-chain swaps.

        Returns:
            Dict[str, Any]: A dictionary containing active orders.
        """
        url = f"{self.base_url}/fusion-plus/orders/{self.api_version}/order/active"
        params = {
            "page": page,
            "limit": limit
        }
        if src_chain is not None:
            params["srcChain"] = src_chain
        if dst_chain is not None:
            params["dstChain"] = dst_chain

        headers = self._get_headers()

        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get active orders: {response.status_code} {response.text}")

    def get_order_status(self, order_hashes: List[str]) -> Dict[str, Any]:
        """
        Get the status of specific orders.

        Args:
            order_hashes (List[str]): A list of order hashes to query.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the orders.
        """
        url = f"{self.base_url}/fusion-plus/orders/{self.api_version}/order/status"
        payload = {
            "orderHashes": order_hashes
        }

        headers = self._get_headers()

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get order status: {response.status_code} {response.text}")

    def get_order_secrets(self, order_hash: str) -> Dict[str, Any]:
        """
        Get all data to perform withdrawal and cancellation for a specific order.

        Args:
            order_hash (str): The order hash to query.

        Returns:
            Dict[str, Any]: A dictionary containing secrets and related data.
        """
        url = f"{self.base_url}/fusion-plus/orders/{self.api_version}/order/secrets/{order_hash}"

        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        if response.status_code in (200, 201):
            return response.json()
        else:
            raise Exception(f"Failed to get order secrets: {response.status_code} {response.text}")

    # Add other methods as needed, following the same pattern.
