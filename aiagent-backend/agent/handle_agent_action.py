import constants
import json
from db.tokens import add_token
from db.nfts import add_nft
from agent.custom_actions.swap_tokens import swap_tokens, fetch_quote, fetch_active_orders
from agent.custom_actions.get_price import get_price_from_pyth

def handle_agent_action(agent_action, content):
    """
    Adds handling for the agent action.
    In our app, we interact with deployed tokens and NFTs, and handle 1inch actions.
    """
    if agent_action == constants.DEPLOY_TOKEN:
        try:
            # Search for contract address from output
            address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
            # Add token to database
            add_token(address)
        except Exception as e:
            print(f"Error deploying token: {e}")
    elif agent_action == constants.DEPLOY_NFT:
        try:
            # Search for contract address from output
            address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
            # Add NFT to database
            add_nft(address)
        except Exception as e:
            print(f"Error deploying NFT: {e}")
    elif agent_action == constants.FETCH_ACTIVE_ORDERS:
        try:
            orders = fetch_active_orders()
            print("Fetched active orders:", orders)
        except Exception as e:
            print(f"Error fetching active orders: {e}")
    elif agent_action == constants.SWAP_TOKENS:
        try:
            params = json.loads(content)
            from_token = params.get('from_token')
            to_token = params.get('to_token')
            amount = float(params.get('amount'))
            slippage = float(params.get('slippage', 100))
            result = swap_tokens(from_token, to_token, amount, slippage)
            print("Swap Tokens Result:", result)
        except Exception as e:
            print(f"Error swapping tokens: {e}")
    elif agent_action == constants.FETCH_QUOTE:
        try:
            params = json.loads(content)
            from_token = params.get('from_token')
            to_token = params.get('to_token')
            amount = float(params.get('amount'))
            quote = fetch_quote(from_token, to_token, amount)
            print("Fetched Quote:", quote)
        except Exception as e:
            print(f"Error fetching quote: {e}")
    elif agent_action == constants.GET_PRICE:
        try:
            params = json.loads(content)
            price_feed_id = params.get('price_feed_id')
            max_age_seconds = int(params.get('max_age_seconds', 600))
            pyth_contract_address = params.get('pyth_contract_address')
            web3_provider_url = params.get('web3_provider_url')
            price_data = get_price_from_pyth(
                price_feed_id, max_age_seconds, pyth_contract_address, web3_provider_url
            )
            # Process the fetched price data
            price = price_data.get('price')
            conf = price_data.get('conf')
            expo = price_data.get('expo')
            publish_time = price_data.get('publishTime')
            print(f"Price: {price}e{expo}")
            print(f"Confidence Interval: {conf}")
            print(f"Publish Time: {publish_time}")
        except Exception as e:
            print(f"Error fetching price data: {e}")
