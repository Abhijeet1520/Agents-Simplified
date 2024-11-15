import constants
import re
from db.tokens import add_token
from db.nfts import add_nft
from agent.oneinch_actions.actions import fetch_active_orders

def handle_agent_action(agent_action, content):
    """
    Adds handling for the agent action.
    In our sample app, we just add deployed tokens and NFTs to the database.
    """
    if agent_action == constants.DEPLOY_TOKEN:
        # Search for contract address from output
        address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
        # Add token to database
        add_token(address)
    if agent_action == constants.DEPLOY_NFT:
        # Search for contract address from output
        address = re.search(r'0x[a-fA-F0-9]{40}', content).group()
        # Add NFT to database
        add_nft(address)
    if agent_action == constants.FETCH_ACTIVE_ORDERS:
        orders = fetch_active_orders()
        print("Fetched active orders:", orders)
