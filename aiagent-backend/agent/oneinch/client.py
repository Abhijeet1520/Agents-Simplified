import os
import requests
from typing import Any, Dict, List, Optional
from web3 import Web3
from eth_account import Account
import hashlib
import random
import string
from dotenv import load_dotenv
from time import sleep

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
        secret_hashes = [HashLock.hash_secret(s) for s in secrets]
        # Compute Merkle root
        secret_hash_bytes = [bytes.fromhex(s[2:]) for s in secret_hashes]
        merkle_root = HashLock.compute_merkle_root(secret_hash_bytes)
        merkle_root_hex = '0x' + merkle_root.hex()
        return {
            "type": "merkle",
            "root": merkle_root_hex
        }

class Preset:
    def __init__(self, preset_data: Dict[str, Any]):
        self.preset_data = preset_data
        self.secretsCount = preset_data.get("secretsCount", 1)
        self.auctionEndAmount = int(preset_data.get("auctionEndAmount", "0"))
        self.allowPartialFills = preset_data.get("allowPartialFills", False)
        self.allowMultipleFills = preset_data.get("allowMultipleFills", False)
        self.exclusiveResolver = preset_data.get("exclusiveResolver")

    def create_auction_details(self, delay: int = 0) -> Dict[str, Any]:
        start_time = int(self.preset_data.get("auctionStartTime", 0)) + delay
        duration = int(self.preset_data.get("auctionDuration", 0))
        end_time = start_time + duration
        return {
            "startTime": start_time,
            "endTime": end_time,
            "auctionEndAmount": self.auctionEndAmount,
        }

class Quote:
    def __init__(self, params: Dict[str, Any], response: Dict[str, Any]):
        self.params = params
        self.srcTokenAmount = int(response["srcTokenAmount"])
        self.dstTokenAmount = int(response["dstTokenAmount"])
        self.presets = {
            "fast": Preset(response["presets"]["fast"]),
            "medium": Preset(response["presets"]["medium"]),
            "slow": Preset(response["presets"]["slow"]),
            # Include custom preset if available
            "custom": Preset(response["presets"]["custom"]) if "custom" in response["presets"] else None
        }
        self.timeLocks = response["timeLocks"]
        self.srcSafetyDeposit = int(response["srcSafetyDeposit"])
        self.dstSafetyDeposit = int(response["dstSafetyDeposit"])
        self.prices = response["prices"]
        self.volume = response["volume"]
        self.quoteId = response.get("quoteId")
        self.whitelist = response["whitelist"]
        self.recommendedPreset = response["recommendedPreset"]
        self.srcEscrowFactory = response["srcEscrowFactory"]
        self.dstEscrowFactory = response["dstEscrowFactory"]

    def get_preset(self, preset_name: str):
        return self.presets.get(preset_name, self.presets[self.recommendedPreset])

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
        fee: Optional[int] = None,
        preset: Optional[str] = None,
    ) -> Quote:
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
            fee (Optional[int]): Fee in basis points (bps).
            preset (Optional[str]): Preset strategy.

        Returns:
            Quote: The quote details.
        """

        url = f"{self.base_url}/quoter/{self.api_version}/quote/receive"
        params = {
            "amount": amount,
            "srcChainId": src_chain_id,
            "dstChainId": dst_chain_id,
            "srcTokenAddress": src_token_address,
            "dstTokenAddress": dst_token_address,
            "walletAddress": wallet_address,
            "enableEstimate": str(enable_estimate).lower(),
            "fee": fee,
            "preset": preset,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        headers = self._get_headers()

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return Quote(params, response.json())
        else:
            raise Exception(f"Failed to get quote: {response.status_code} {response.text}")

    def create_order(
        self,
        quote: Quote,
        secrets: List[str],
        preset_name: str,
        wallet_address: str,
        receiver_address: Optional[str] = None,
        fee_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an order and sign it using EIP-712.

        Args:
            quote (Quote): Quote object.
            secrets (List[str]): List of secrets for hash lock.
            preset_name (str): Preset strategy.
            wallet_address (str): Wallet address.
            receiver_address (Optional[str]): Receiver address.
            fee_info (Optional[Dict[str, Any]]): Fee information.

        Returns:
            Dict[str, Any]: Order details including the hash and signature.
        """
        # Select the preset
        preset = quote.get_preset(preset_name)

        # Create auction details
        auction_details = preset.create_auction_details()

        # Determine nonce
        allow_partial_fills = preset.allowPartialFills
        allow_multiple_fills = preset.allowMultipleFills
        nonce_required = not (allow_partial_fills and allow_multiple_fills)
        nonce = random.randint(1, 2**40 - 1) if nonce_required else None

        # Create hashLock object
        if len(secrets) == 1:
            hash_lock = HashLock.for_single_fill(secrets[0])
        else:
            hash_lock = HashLock.for_multiple_fills(secrets)

        # Prepare order parameters
        order = {
            "makerAsset": quote.params["srcTokenAddress"],
            "takerAsset": quote.params["dstTokenAddress"],
            "makingAmount": str(quote.srcTokenAmount),
            "takingAmount": str(preset.auctionEndAmount),
            "maker": wallet_address,
            "receiver": receiver_address or wallet_address,
            "allowedSender": "0x0000000000000000000000000000000000000000",
            "salt": hex(nonce) if nonce else hex(random.randint(1, 2**256 - 1)),
            "predicate": "0x",  # Placeholder; may need actual data
            "permit": "0x",     # Placeholder; may need actual data
            "interaction": "0x",  # Placeholder; may need actual data
        }

        # Define EIP-712 domain and types
        chain_id = int(quote.params["srcChainId"])
        verifying_contract = quote.srcEscrowFactory
        eip712_domain = {
            "name": "1inch Cross Chain",
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": verifying_contract,
        }

        eip712_types = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Order": [
                {"name": "salt", "type": "uint256"},
                {"name": "maker", "type": "address"},
                {"name": "receiver", "type": "address"},
                {"name": "allowedSender", "type": "address"},
                {"name": "makingAmount", "type": "uint256"},
                {"name": "takingAmount", "type": "uint256"},
                {"name": "makerAsset", "type": "address"},
                {"name": "takerAsset", "type": "address"},
                {"name": "getMakerAmount", "type": "bytes"},
                {"name": "getTakerAmount", "type": "bytes"},
                {"name": "predicate", "type": "bytes"},
                {"name": "permit", "type": "bytes"},
                {"name": "interaction", "type": "bytes"},
            ]
        }

        # Prepare the order data for signing
        order_message = {
            "salt": int(order["salt"], 16),
            "maker": order["maker"],
            "receiver": order["receiver"],
            "allowedSender": order["allowedSender"],
            "makingAmount": int(order["makingAmount"]),
            "takingAmount": int(order["takingAmount"]),
            "makerAsset": order["makerAsset"],
            "takerAsset": order["takerAsset"],
            "getMakerAmount": order.get("getMakerAmount", "0x"),
            "getTakerAmount": order.get("getTakerAmount", "0x"),
            "predicate": order.get("predicate", "0x"),
            "permit": order.get("permit", "0x"),
            "interaction": order.get("interaction", "0x"),
        }

        # Create the EIP-712 structured data
        structured_data = {
            "types": eip712_types,
            "domain": eip712_domain,
            "primaryType": "Order",
            "message": order_message,
        }

        # # Encode the structured data
        # encoded_data = encode_structured_data(structured_data)

        # Sign the message
        signed_message = Account.sign_message(structured_data, private_key=self.private_key)
        signature = signed_message.signature.hex()

        # Attach the signature to the order
        order["signature"] = signature

        # Prepare additional data for submission
        order_data = {
            "order": order,
            "hash": None,  # The hash can be calculated if needed
            "quoteId": quote.quoteId,
            "secretHashes": [HashLock.hash_secret(s) for s in secrets],
        }

        return order_data

    def submit_order(
        self, src_chain_id: int, order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit an order to the API.

        Args:
            src_chain_id (int): Source chain ID.
            order_data (Dict[str, Any]): Order data including order, quoteId, secretHashes.

        Returns:
            Dict[str, Any]: API response.
        """
        url = f"{self.base_url}/relayer/{self.api_version}/order/submit"
        payload = {
            "srcChainId": src_chain_id,
            "order": order_data["order"],
            "quoteId": order_data["quoteId"],
            "secretHashes": order_data["secretHashes"],
        }
        headers = self._get_headers()

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Failed to submit order: {response.status_code} {response.text}")

    # ... (Other methods remain the same)

def main():
    # Setup
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not private_key:
        raise ValueError("WALLET_PRIVATE_KEY environment variable not set.")
    client = OneInchClient(private_key=private_key)
    wallet_address = client.account.address

    # Parameters
    amount = "1000000000000000000"  # 1 ETH (in wei)
    src_chain_id = 1     # Ethereum
    dst_chain_id = 137   # Polygon
    src_token_address = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"  # ETH
    dst_token_address = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"  # WETH on Polygon
    source = "sdk-tutorial"
    preset = "fast"
    fee_bps = 100  # 1%

    # Step 1: Get a quote
    quote = client.get_quote(
        amount, src_chain_id, dst_chain_id, src_token_address, dst_token_address, wallet_address, fee=fee_bps, preset=preset
    )
    print("Quote received.")

    # Step 2: Generate secrets
    secrets_count = quote.get_preset(preset).secretsCount
    secrets = [
        "0x" + "".join(random.choices(string.hexdigits.lower(), k=64)) for _ in range(secrets_count)
    ]

    # Step 3: Create order (signing included)
    order_data = client.create_order(quote, secrets, preset, wallet_address)
    print("Order created and signed.")

    # Step 4: Submit order
    order_response = client.submit_order(
        src_chain_id, order_data
    )
    print("Order submitted.")

    # Step 5: Monitor and submit secrets
    order_hash = order_response.get("hash") or order_data["order"]["hash"]
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
            sleep(10)
        except Exception as e:
            print("Error:", str(e))
            sleep(10)

    print("Order status:", client.get_order_status(order_hash))

if __name__ == "__main__":
    main()
