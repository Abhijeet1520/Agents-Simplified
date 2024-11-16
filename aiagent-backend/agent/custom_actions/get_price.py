from web3 import Web3
from typing import Any, Dict
import os
import json
import dotenv
from pythclient.pythclient import PythClient
import asyncio

dotenv.load_dotenv()

def get_price_from_pyth(price_feed_id: str, max_age_seconds: int, pyth_contract_address:str = '0x8250f4aF4B972684F7b336503E2D6dFeDeB1487a', web3_provider_url: str = 'https://mainnet.base.org') -> Dict[str, Any]:
    """
    Fetch the latest price from the Pyth contract using getPriceNoOlderThan.

    Args:
        price_feed_id (str): The ID of the price feed to read.
        max_age_seconds (int): Maximum age of the on-chain price in seconds.

    Returns:
        Dict[str, Any]: A dictionary containing price, conf, expo, and publishTime.
    """
    w3 = Web3(Web3.HTTPProvider(web3_provider_url))

    # Check connection
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to the network.")

    network_id = w3.eth.chain_id
    print(f"Connected to network ID: {network_id}")

    # Load the Pyth contract ABI
    abi_path = os.path.join(os.path.dirname(__file__), 'pyth_abi.json')
    with open(abi_path, 'r') as abi_file:
        pyth_abi = json.load(abi_file)

    # Instantiate the Pyth contract
    pyth_contract = w3.eth.contract(address=pyth_contract_address, abi=pyth_abi)

    # Convert price_feed_id to bytes32
    price_feed_id_bytes = bytes.fromhex(price_feed_id[2:])  # Remove '0x' prefix if present

    # Call getPriceNoOlderThan
    result = pyth_contract.functions.getPriceNoOlderThan(price_feed_id_bytes, max_age_seconds).call()

    price = result[0]
    conf = result[1]
    expo = result[2]
    publishTime = result[3]

    async def fetch_price():
        async with PythClient() as client:
            await client.refresh_all_prices()
            price_account = client.price_accounts.get(price_feed_id)
            if not price_account:
                raise ValueError(f"Price feed {price_feed_id} not found.")
            price_data = price_account.aggregate_price
            return {
                'price': price_data.price,
                'conf': price_data.confidence_interval,
                'expo': price_data.exponent,
                'publishTime': price_data.publish_time
            }
    return asyncio.run(fetch_price())

if __name__ == "__main__":
    # Example usage
    price_feed_id = "0x2817d7bfe5c64b8ea956e9a26f573ef64e72e4d7891f2d6af9bcc93f7aff9a97"  # Example price feed ID
    max_age_seconds = 6000  # Maximum age in seconds

    try:
        price_data = get_price_from_pyth(price_feed_id, max_age_seconds)
        print("Price data fetched successfully:")
        print(price_data)
    except Exception as e:
        print(f"Error fetching price data: {e}")
