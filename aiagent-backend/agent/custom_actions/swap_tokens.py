from web3 import Web3
from typing import Any, Dict
import os
import json
import time

def swap_tokens(token_in_address: str, token_out_address: str, amount_in_wei: int, slippage: float) -> Dict[str, Any]:
    """
    Swap tokens on the Base Sepolia network using a DEX.

    Args:
        token_in_address (str): Address of the input ERC-20 token.
        token_out_address (str): Address of the output ERC-20 token.
        amount_in_wei (int): Amount of the input token to swap (in Wei).
        slippage (float): Maximum acceptable slippage percentage (e.g., 0.5 for 0.5%).

    Returns:
        Dict[str, Any]: Transaction receipt or relevant swap information.
    """
    # Connect to Base Sepolia network
    base_sepolia_rpc = "https://sepolia.base.org"
    w3 = Web3(Web3.HTTPProvider(base_sepolia_rpc))

    # Check connection
    if not w3.isConnected():
        raise Exception("Failed to connect to Base Sepolia network")

    # Set up account (ensure the private key is securely managed)
    private_key = os.getenv('PRIVATE_KEY')  # PRIVATE_KEY should be set in environment variables
    if not private_key:
        raise Exception("Private key not found in environment variables")
    account = w3.eth.account.from_key(private_key)
    w3.eth.default_account = account.address

    # Load ERC-20 token ABI
    with open('erc20_abi.json', 'r') as abi_file:
        erc20_abi = json.load(abi_file)

    # Load ERC-20 token contracts
    token_in_contract = w3.eth.contract(address=token_in_address, abi=erc20_abi)
    token_out_contract = w3.eth.contract(address=token_out_address, abi=erc20_abi)

    # Load DEX router contract (provide DEX router ABI and address)
    dex_router_address = '0xYourDEXRouterAddress'  # Replace with actual DEX router address
    with open('dex_router_abi.json', 'r') as abi_file:
        dex_router_abi = json.load(abi_file)
    dex_router_contract = w3.eth.contract(address=dex_router_address, abi=dex_router_abi)

    # Approve DEX router to spend the input tokens
    nonce = w3.eth.get_transaction_count(account.address)
    approve_txn = token_in_contract.functions.approve(
        dex_router_address,
        amount_in_wei
    ).buildTransaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.toWei('5', 'gwei')
    })
    signed_approve_txn = w3.eth.account.sign_transaction(approve_txn, private_key=private_key)
    approve_tx_hash = w3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(approve_tx_hash)

    # Calculate minimum amount out based on slippage
    amounts_out = dex_router_contract.functions.getAmountsOut(
        amount_in_wei,
        [token_in_address, token_out_address]
    ).call()
    min_amount_out = int(amounts_out[-1] * (1 - slippage / 100))

    # Perform the swap
    swap_txn = dex_router_contract.functions.swapExactTokensForTokens(
        amount_in_wei,
        min_amount_out,
        [token_in_address, token_out_address],
        account.address,
        int(time.time()) + 300  # Deadline set to 5 minutes from now
    ).buildTransaction({
        'from': account.address,
        'nonce': nonce + 1,
        'gas': 200000,
        'gasPrice': w3.toWei('5', 'gwei')
    })
    signed_swap_txn = w3.eth.account.sign_transaction(swap_txn, private_key=private_key)
    swap_tx_hash = w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

    # Wait for transaction receipt
    swap_receipt = w3.eth.wait_for_transaction_receipt(swap_tx_hash)

    # Return transaction receipt or relevant information
    return {
        'transactionHash': swap_receipt.transactionHash.hex(),
        'status': swap_receipt.status
    }
