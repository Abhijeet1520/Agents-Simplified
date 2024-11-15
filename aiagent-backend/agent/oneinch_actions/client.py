import os
import time
import json
import requests
from typing import Any, Dict
from web3 import Web3

class OneInchClient:
    def __init__(self):
        """
        Initialize the OneInchClient with necessary configurations.
        """
        self.base_sepolia_rpc = "https://sepolia.base.org"
        self.w3 = Web3(Web3.HTTPProvider(self.base_sepolia_rpc))
        if not self.w3.isConnected():
            raise Exception("Failed to connect to Base Sepolia network")

        # Load wallet private key
        self.private_key = os.getenv('PRIVATE_KEY')
        if not self.private_key:
            raise Exception("Private key not found in environment variables")
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.w3.eth.default_account = self.account.address

        # Load API Key
        self.api_key = os.getenv('ONEINCH_API_KEY')
        if not self.api_key:
            raise Exception("1inch API key not found in environment variables")

        # Load ERC-20 ABI
        with open('erc20_abi.json', 'r') as abi_file:
            self.erc20_abi = json.load(abi_file)

        # Load DEX Router ABI and Address
        self.dex_router_address = '0xYourDEXRouterAddress'  # Replace with your DEX router address
        with open('dex_router_abi.json', 'r') as abi_file:
            self.dex_router_abi = json.load(abi_file)

    def swap_tokens(self, token_in_address: str, token_out_address: str, amount_in_wei: int, slippage: float) -> Dict[str, Any]:
        # ...existing code...
        pass  # Rest of the swap_tokens method

    def get_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # ...existing code...
        pass  # Rest of the get_quote method

    def fetch_active_orders(self) -> Dict[str, Any]:
        """
        Fetch active orders from the 1inch Fusion+ API.
        """
        api_url = "https://api.1inch.dev/fusion-plus/orders/v1.0/order/active"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch active orders: {response.status_code} {response.text}")
