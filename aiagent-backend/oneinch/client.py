import os
import requests
import constants
from typing import Any, Dict, List, Optional
from web3 import Web3
from eth_account import Account
import random
import time
from eth_account.messages import encode_typed_data
import json
from db.wallet import get_wallet_info, add_wallet_info

class NetworkEnum:
    ETHEREUM = 1
    ARBITRUM = 42161
    COINBASE = 8453
    BASE_SEPOLIA = 84532

class OneInchClient:
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize the OneInchClient.
        """
        try:
            self.base_url = "https://api.1inch.dev"
            self.fusion_plus_url = f"{self.base_url}/fusion-plus"
            self.api_version = "v1.0"

            web3_provider = os.getenv("WEB3_PROVIDER_URL", "https://sepolia.base.org")
            self.w3 = Web3(Web3.HTTPProvider(web3_provider))
            self.api_key = os.getenv("ONEINCH_API_KEY", "")
            self.private_key = private_key or os.getenv("WALLET_PRIVATE_KEY")

            # Load wallet info from the database
            self.load_wallet_info()

            if not self.private_key:
                self.account = Account.create()
                self.address = self.account.address
                self.private_key = self.account.key.hex()
            else:
                self.account = Account.from_key(self.private_key)
                self.address = self.account.address

            print(f"Initialized with address: {self.address}")
        except Exception as e:
            print(f"Init error: {e}")
            self.w3 = None
            self.account = None
            self.address = None

    def _save_wallet_info(self):
        """
        Save wallet information to the database.
        """
        wallet_info = {
            "wallet_id": self.address,
            "seed": self.private_key
        }
        add_wallet_info(json.dumps(wallet_info))

    def load_wallet_info(self):
        """
        Load wallet information from the database.
        """
        try:
            # Read wallet data from environment variable or database
            wallet_id = os.getenv(constants.WALLET_ID_ENV_VAR)
            wallet_seed = os.getenv(constants.WALLET_SEED_ENV_VAR)
            wallet_info = json.loads(get_wallet_info()) if get_wallet_info() else None

            # Configure CDP Agentkit Langchain Extension.
            values = {}

            # Load agent wallet information from database or environment variables
            if wallet_info:
                wallet_id = wallet_info["wallet_id"]
                wallet_seed = wallet_info["seed"]
                self.address = wallet_info["default_address_id"]
                self.private_key = wallet_seed
                values = {"cdp_wallet_data": json.dumps({ "wallet_id": wallet_id, "seed": wallet_seed })}
            elif wallet_id and wallet_seed:
                self.address = wallet_id
                self.private_key = wallet_seed
                values = {"cdp_wallet_data": json.dumps({ "wallet_id": wallet_id, "seed": wallet_seed })}

            if self.private_key:
                self.account = Account.from_key(self.private_key)
                print(f"Loaded wallet info for address: {self.address}")
            else:
                print("No wallet info found in the database.")
        except Exception as e:
            print(f"Load wallet info error: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.
        """
        try:
            return {
                "accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            print(f"Headers error: {e}")
            return {}

    def _sign_typed_data(self, data: Dict) -> str:
        """
        Sign typed data using EIP-712 standard.
        """
        try:
            signable_message = encode_typed_data(
                domain_data=data.get("domain"),
                message_types=data.get("types"),
                message_data=data.get("message")
            )
            signature = self.account.sign_message(signable_message)
            return signature.signature.hex()
        except Exception as e:
            print(f"Signing error: {e}")
            return ""

    def get_quote(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a quote for token swap.
        """
        try:
            url = f"{self.fusion_plus_url}/quote/{self.api_version}"
            response = requests.post(
                url,
                headers=self._get_headers(),
                json={
                    "fromTokenAddress": params.get("from_token"),
                    "toTokenAddress": params.get("to_token"),
                    "amount": str(params.get("amount")),
                    "walletAddress": self.address
                }
            )
            return response.json() if response.ok else {}
        except Exception as e:
            print(f"Quote error: {e}")
            return {}

    def swap_tokens(self, from_token: str, to_token: str, amount: int, recipient: str, slippage: float) -> Dict[str, Any]:
        """
        Swap tokens using OneInchClient.
        """
        try:
            params = {
                "from_token": from_token,
                "to_token": to_token,
                "amount": amount,
                "recipient": recipient,
                "slippage": slippage
            }
            url = f"{self.fusion_plus_url}/swap/{self.api_version}"
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=params
            )
            return response.json() if response.ok else {}
        except Exception as e:
            print(f"Swap tokens error: {e}")
            return {}

    def create_order(self, quote_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an order using a quote.
        """
        try:
            secret = "0x" + hex(random.getrandbits(256))[2:].zfill(64)

            url = f"{self.fusion_plus_url}/orders/{self.api_version}/create"
            payload = {
                "quoteId": quote_id,
                "secret": secret,
                **params
            }

            response = requests.post(url, headers=self._get_headers(), json=payload)
            result = response.json() if response.ok else {}

            if result.get("orderHash"):  # Store secret if order created
                result["secret"] = secret

            return result
        except Exception as e:
            print(f"Create order error: {e}")
            return {}

    def get_order_status(self, order_hash: str) -> Dict[str, Any]:
        """
        Get the status of an order.
        """
        try:
            url = f"{self.fusion_plus_url}/orders/{self.api_version}/status"
            response = requests.get(
                url,
                headers=self._get_headers(),
                params={"orderHash": order_hash}
            )
            return response.json() if response.ok else {}
        except Exception as e:
            print(f"Status error: {e}")
            return {}

    def submit_secret(self, order_hash: str, secret: str) -> Dict[str, Any]:
        """
        Submit a secret to execute an order.
        """
        try:
            url = f"{self.fusion_plus_url}/orders/{self.api_version}/submit-secret"
            payload = {
                "orderHash": order_hash,
                "secret": secret
            }
            response = requests.post(url, headers=self._get_headers(), json=payload)
            return response.json() if response.ok else {}
        except Exception as e:
            print(f"Submit secret error: {e}")
            return {}

def test_client():
    """
    Test the OneInchClient functionality.
    """
    try:
        client = OneInchClient()

        # Test parameters
        params = {
            "from_token": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            "to_token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "amount": "1000000"
        }

        # Test quote
        print("Getting quote...")
        quote = client.get_quote(params)

        if quote.get("quoteId"):
            print(f"Quote received: {quote['quoteId']}")

            # Create order
            order = client.create_order(quote["quoteId"], {
                "fromTokenAddress": params["from_token"],
                "toTokenAddress": params["to_token"],
                "amount": params["amount"]
            })

            if order.get("orderHash"):
                print(f"Order created: {order['orderHash']}")

                # Poll status 3 times
                for i in range(3):
                    status = client.get_order_status(order["orderHash"])
                    print(f"Status {i+1}: {status.get('status', 'unknown')}")
                    time.sleep(2)

                    if status.get("status") == "ready":
                        print("Submitting secret...")
                        result = client.submit_secret(
                            order["orderHash"],
                            order["secret"]
                        )
                        print(f"Secret submitted: {result}")
                        break
            else:
                print("Order creation failed")
        else:
            print("Quote failed")

    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    test_client()
