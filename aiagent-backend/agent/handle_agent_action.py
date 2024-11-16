import constants
import json
from db.tokens import add_token
from db.nfts import add_nft
from agent.custom_actions.swap_tokens import swap_tokens, fetch_quote, fetch_active_orders

def handle_agent_action(agent_action, content):
    """
    Adds handling for the agent action.
    In our app, we interact with deployed tokens and NFTs, and handle 1inch actions.
    """
    if agent_action == constants.DEPLOY_TOKEN:
        # Search for contract address from output
        address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
        # Add token to database
        add_token(address)
    elif agent_action == constants.DEPLOY_NFT:
        # Search for contract address from output
        address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
        # Add NFT to database
        add_nft(address)
    elif agent_action == constants.FETCH_ACTIVE_ORDERS:
        orders = fetch_active_orders()
        print("Fetched active orders:", orders)
    elif agent_action == constants.SWAP_TOKENS:
        params = json.loads(content)
        from_token = params.get('from_token')
        to_token = params.get('to_token')
        amount = float(params.get('amount'))
        slippage = float(params.get('slippage', 0.5))
        result = swap_tokens(from_token, to_token, amount, slippage)
        print("Swap Tokens Result:", result)
    elif agent_action == constants.FETCH_QUOTE:
        params = json.loads(content)
        from_token = params.get('from_token')
        to_token = params.get('to_token')
        amount = float(params.get('amount'))
        quote = fetch_quote(from_token, to_token, amount)
        print("Fetched Quote:", quote)
