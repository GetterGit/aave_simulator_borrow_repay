from brownie import accounts
from scripts.helpful_scripts import get_account
from brownie import interface, network, config
from web3 import Web3


def get_weth():
    """Mints WETH when depositing ETH
    We will need our script to be able to call the WETH contract"""
    # ABI comes from the IWETH interface
    # Address comes from our config depending on the chain we are working on
    account = get_account()
    # below, we get a weth contract for respective network based on the ABI from the interface + address from our config file
    weth = interface.WethInterface(
        config["networks"][network.show_active()]["weth_token"]
    )
    # after depositing N ETH, we should get N WETH in return
    deposit_tx = weth.deposit({"from": account, "value": Web3.toWei(0.001, "ether")})
    deposit_tx.wait(1)
    print("Received 0.001 WETH")
    return deposit_tx


def main():
    get_weth()
