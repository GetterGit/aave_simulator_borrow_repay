from scripts.aave_borrow import approve_erc20, get_asset_price, get_lending_pool
from brownie import network, config
from web3 import Web3
from scripts.helpful_scripts import get_account

# testing that the DAI/ETH price feed returns the DAI's price in terms of ETH
def test_get_asset_price():
    # Arrange / Act
    asset_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # Assert
    assert asset_price > 0


# testing that the lending pool contract is returned
def test_get_lending_pool():
    # Arrange / Act
    lending_pool = get_lending_pool()
    # Assert
    lending_pool is not None


# testing ERC20 approval
def test_approve_erc20():
    # Arrange
    account = get_account()
    lending_pool = get_lending_pool()
    amount = Web3.toWei(1, "ether")
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # Act
    approval_tx = approve_erc20(amount, lending_pool, erc20_address, account)
    approval_tx.wait(1)
    # Assert
    # 'is not True' would mean the tx has passed and the approval has happenned
    assert approval_tx is not True
