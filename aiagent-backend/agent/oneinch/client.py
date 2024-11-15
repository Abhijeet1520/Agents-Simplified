import os
import requests
from typing import Any, Dict, List, Optional
from web3 import Web3
from eth_account import Account
import hashlib
from time import sleep
import random
import string
from dotenv import load_dotenv

load_dotenv()

class HashLock:
    @staticmethod
    def hash_secret(secret: str) -> str:
        secret_bytes = bytes.fromhex(secret[2:])
        secret_hash_bytes = hashlib.sha256(secret_bytes).digest()
        return '0x' + secret_hash_bytes.hex()

    @staticmethod
    def for_single_fill(secret: str) -> Dict[str, Any]:
        secret_hash = HashLock.hash_secret(secret)
        return {
            "type": "single",
            "secretHash": secret_hash
        }

    @staticmethod
    def compute_merkle_root(leaves: List[bytes]) -> bytes:
        if len(leaves) == 0:
            return b'\x00' * 32
        elif len(leaves) == 1:
            return leaves[0]
        else:
            while len(leaves) > 1:
                if len(leaves) % 2 != 0:
                    leaves.append(leaves[-1])
                new_leaves = []
                for i in range(0, len(leaves), 2):
                    combined = leaves[i] + leaves[i+1]
                    new_leaf = hashlib.sha256(combined).digest()
                    new_leaves.append(new_leaf)
                leaves = new_leaves
            return leaves[0]

    @staticmethod
    def for_multiple_fills(secrets: List[str]) -> Dict[str, Any]:
        # Compute secret hashes
        secret_hashes = [bytes.fromhex(HashLock.hash_secret(s)[2:]) for s in secrets]
        # Compute Merkle root
        merkle_root = HashLock.compute_merkle_root(secret_hashes)
        merkle_root_hex = '0x' + merkle_root.hex()
        return {
            "type": "merkle",
            "root": merkle_root_hex
        }


class OneInchClient:
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize the OneInchClient.

        Args:
            private_key (Optional[str]): The private key of the wallet to sign transactions.
        """
        self.base_url = "https://api.1inch.dev/fusion-plus"
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
            self.private_key = self.account.key.hex()

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

    def get_quote(
        self,
        amount: str,
        src_chain_id: int,
        dst_chain_id: int,
        src_token_address: str,
        dst_token_address: str,
        wallet_address: str,
        enable_estimate: bool = False,
    ) -> Dict[str, Any]:
        """
        Get a cross-chain swap quote.

        Args:
            amount (str): The amount to be swapped.
            src_chain_id (int): Source chain ID.
            dst_chain_id (int): Destination chain ID.
            src_token_address (str): Source token address.
            dst_token_address (str): Destination token address.
            wallet_address (str): Wallet address for the swap.
            enable_estimate (bool): Whether to enable estimate.

        Returns:
            Dict[str, Any]: The quote details.
        """

        url = f"{self.base_url}/quoter/{self.api_version}/quote/receive"
        params = {
            "amount": amount,
            "srcChain": src_chain_id,
            "dstChain": dst_chain_id,
            "srcTokenAddress": src_token_address,
            "dstTokenAddress": dst_token_address,
            "walletAddress": wallet_address,
            "enableEstimate": str(enable_estimate).lower()
        }
        headers = self._get_headers()

        response = requests.get(url, params=params, headers=headers)

        # For debugging purposes
        print(f"GET {response.url}")
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get quote: {response.status_code} {response.text}")

    def create_order(
        self,
        quote: Dict[str, Any],
        secrets: List[str],
        preset: str,
        source: str,
        wallet_address: str
    ) -> Dict[str, Any]:
        """
        Create an order.

        Args:
            quote (Dict[str, Any]): Quote information.
            secrets (List[str]): List of secrets for hash lock.
            preset (str): Preset strategy.
            source (str): Source identifier.
            wallet_address (str): Wallet address.

        Returns:
            Dict[str, Any]: Order details including the hash.
        """
        url = f"{self.base_url}/relayer/{self.api_version}/order/create"

        # Create hashLock object
        if len(secrets) == 1:
            hash_lock = HashLock.for_single_fill(secrets[0])
        else:
            hash_lock = HashLock.for_multiple_fills(secrets)

        payload = {
            "quote": quote,
            "hashLock": hash_lock,
            "preset": preset,
            "source": source,
            "walletAddress": wallet_address
        }
        headers = self._get_headers()

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create order: {response.status_code} {response.text}")

    def submit_order(
        self, src_chain_id: int, order: Dict[str, Any], quote_id: str, secret_hashes: List[str]
    ) -> Dict[str, Any]:
        """
        Submit an order to the API.

        Args:
            src_chain_id (int): Source chain ID.
            order (Dict[str, Any]): Order data.
            quote_id (str): Quote ID.
            secret_hashes (List[str]): Secret hashes for hash lock.

        Returns:
            Dict[str, Any]: API response.
        """
        url = f"{self.base_url}/{self.api_version}/order/submit"
        payload = {
            "srcChainId": src_chain_id,
            "order": order,
            "quoteId": quote_id,
            "secretHashes": secret_hashes
        }
        headers = self._get_headers()

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to submit order: {response.status_code} {response.text}")

    def submit_secret(self, order_hash: str, secret: str) -> None:
        """
        Submit a secret for a specific order.

        Args:
            order_hash (str): The order hash.
            secret (str): The secret to be submitted.
        """
        url = f"{self.base_url}/{self.api_version}/order/submit-secret"
        payload = {"orderHash": order_hash, "secret": secret}
        headers = self._get_headers()

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to submit secret: {response.status_code} {response.text}")

    def get_order_status(self, order_hash: str) -> Dict[str, Any]:
        """
        Get the status of a specific order.

        Args:
            order_hash (str): The order hash.

        Returns:
            Dict[str, Any]: The status of the order.
        """
        url = f"{self.base_url}/{self.api_version}/order/status/{order_hash}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get order status: {response.status_code} {response.text}")

    def get_ready_to_accept_secret_fills(self, order_hash: str) -> Dict[str, Any]:
        """
        Get fills that are ready to accept secrets for a specific order.

        Args:
            order_hash (str): The order hash.

        Returns:
            Dict[str, Any]: Information about fills ready to accept secrets.
        """
        url = f"{self.base_url}/{self.api_version}/order/ready-to-accept-secret-fills/{order_hash}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get ready to accept secret fills: {response.status_code} {response.text}")


def main():
    # Setup
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    # if not private_key:
    #     raise ValueError("WALLET_PRIVATE_KEY environment variable not set.")
    client = OneInchClient(private_key=private_key)
    wallet_address = client.account.address

    # Parameters
    amount = "100000000000000000"  # 100 USDT (in smallest unit)
    src_chain_id = 1     # Etherium
    dst_chain_id = 137   # Polygon
    src_token_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    dst_token_address = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
    source = "sdk-tutorial"
    preset = "fast"

    # Step 1: Get a quote
    quote = client.get_quote(
        amount, src_chain_id, dst_chain_id, src_token_address, dst_token_address, wallet_address
    )
    print("Quote received:", quote)

    # Step 2: Generate secrets
    secrets = [
        "0x" + "".join(random.choices(string.hexdigits.lower(), k=64)) for _ in range(quote["presets"][preset]["secretsCount"])
    ]
    # Generate secret hashes
    secret_hashes = [HashLock.hash_secret(secret) for secret in secrets]

    # Step 3: Create order
    order_data = client.create_order(quote, secrets, preset, source, wallet_address)
    print("Order created:", order_data)

    # Step 4: Submit order
    order_response = client.submit_order(
        src_chain_id, order_data["order"], order_data["quoteId"], secret_hashes
    )
    print("Order submitted:", order_response)

    # Step 5: Monitor and submit secrets
    order_hash = order_data["hash"]
    while True:
        try:
            # Get fills ready to accept secrets
            secrets_to_share = client.get_ready_to_accept_secret_fills(order_hash)
            fills = secrets_to_share.get("fills", [])
            if fills:
                for fill in fills:
                    idx = fill.get("idx")
                    if idx is not None:
                        secret = secrets[idx]
                        client.submit_secret(order_hash, secret)
                        print(f"Shared secret for fill index {idx}")
            # Check order status
            status_response = client.get_order_status(order_hash)
            status = status_response.get("status")
            if status in ["Executed", "Expired", "Refunded"]:
                break
            client.sleep(10)
        except Exception as e:
            print("Error:", str(e))
            client.sleep(10)

    print("Order status:", client.get_order_status(order_hash))


if __name__ == "__main__":
    main()
