import re
import json
import constants
from db.tokens import add_token
from db.nfts import add_nft
from oneinch.actions import (
    swap_tokens,
    get_quote as fetch_quote,
    fetch_active_orders
)
from agent.custom_actions.get_price import get_price_from_pyth

def handle_agent_action(agent_action: str, content: str) -> None:
    """
    Handle various agent actions including token/NFT deployments and DeFi operations.

    This function processes different types of agent actions and performs the corresponding
    operations such as token deployments, NFT deployments, 1inch trades, and price queries.

    Args:
        agent_action (str): The type of action to be performed (e.g., DEPLOY_TOKEN, SWAP_TOKENS)
        content (str): The content/parameters required for the action, usually in JSON format

    Actions supported:
        - DEPLOY_TOKEN: Deploy a new token contract
        - DEPLOY_NFT: Deploy a new NFT contract
        - FETCH_ACTIVE_ORDERS: Get active orders from 1inch
        - SWAP_TOKENS: Execute a token swap on 1inch
        - FETCH_QUOTE: Get a quote for a token swap
        - GET_PRICE: Get price data from Pyth Network
    """
    if agent_action == constants.DEPLOY_TOKEN:
        try:
            address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
            add_token(address)
        except Exception as e:
            print(f"Error deploying token: {e}")

    if agent_action == constants.DEPLOY_NFT:
        try:
            address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
            add_nft(address)
        except Exception as e:
            print(f"Error deploying NFT: {e}")

    if agent_action == constants.FETCH_ACTIVE_ORDERS:
        try:
            orders = fetch_active_orders()
            print("Active orders:", orders)
        except Exception as e:
            print(f"Error fetching active orders: {e}")

    if agent_action == constants.SWAP_TOKENS:
        try:
            params = json.loads(content)
            result = swap_tokens(
                token_in_address=params.get('from_token'),
                token_out_address=params.get('to_token'),
                amount_in_wei=int(params.get('amount')),
                slippage=float(params.get('slippage', 100))
            )
            print("Swap result:", result)
        except Exception as e:
            print(f"Error swapping tokens: {e}")

    if agent_action == constants.FETCH_QUOTE:
        try:
            params = json.loads(content)
            quote = fetch_quote(
                from_token=params.get('from_token'),
                to_token=params.get('to_token'),
                amount=int(params.get('amount'))
            )
            print("Quote:", quote)
        except Exception as e:
            print(f"Error fetching quote: {e}")

    if agent_action == constants.GET_PRICE:
        try:
            params = json.loads(content)
            price_data = get_price_from_pyth(
                price_feed_id=params.get('price_feed_id'),
                max_age_seconds=int(params.get('max_age_seconds', 600)),
                pyth_contract_address=params.get('pyth_contract_address', '0x8250f4aF4B972684F7b336503E2D6dFeDeB1487a'),
                web3_provider_url=params.get('web3_provider_url', 'https://mainnet.base.org')
            )
            print(f"Price: {price_data.get('price')}e{price_data.get('expo')}")
            print(f"Confidence: {price_data.get('conf')}")
            print(f"Publish Time: {price_data.get('publishTime')}")
        except Exception as e:
            print(f"Error fetching price data: {e}")
