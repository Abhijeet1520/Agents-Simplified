# test.py

import os
from time import sleep
from client import OneInchClient

# Set environment variables (replace with your actual keys)
os.environ["WEB3_PROVIDER_URL"] = "https://mainnet.infura.io/v3/your_infura_project_id"

def main():
    # Initialize the client with your private key
    private_key = os.getenv('PRIVATE_KEY')
    client = OneInchClient(private_key=private_key)

    # Test get_active_orders
    try:
        active_orders = client.get_active_orders(
            page=1,
            limit=10,
            src_chain=1,      # Ethereum Mainnet
            dst_chain=137     # Polygon Network
        )
        print("Active Orders:")
        print(active_orders)
    except Exception as e:
        print(f"Error fetching active orders: {e}")

    sleep(0.2)
    # Test get_order_status
    try:
        order_hashes = [
            "0x10ea5bd12b2d04566e175de24c2df41a058bf16df4af3eb2fb9bff38a9da98e9",
            "0x20ea5bd12b2d04566e175de24c2df41a058bf16df4af3eb2fb9bff38a9da98e8",
        ]
        order_status = client.get_order_status(order_hashes)
        print("\nOrder Status:")
        print(order_status)
    except Exception as e:
        print(f"Error fetching order status: {e}")

    sleep(0.2)
    # Test get_order_secrets
    try:
        order_hash = "0xa0ea5bd12b2d04566e175de24c2df41a058bf16df4af3eb2fb9bff38a9da98e9"
        order_secrets = client.get_order_secrets(order_hash)
        print("\nOrder Secrets:")
        print(order_secrets)
    except Exception as e:
        print(f"Error fetching order secrets: {e}")

if __name__ == "__main__":
    main()
