from brownie import config, network, interface
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account
from web3 import Web3

# setting 0.001 as the amount of WETH to deposit to the Aave protocol
AMOUNT_TO_DEPOSIT = Web3.toWei(0.001, "ether")


def borrow():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # now, we wanna get some weth if testing locally
    if network.show_active() == "mainnet-fork":
        get_weth()
    # now, we can supply WETH to the lending protocol
    # ABI
    # address
    lending_pool = get_lending_pool()
    print(lending_pool)
    # now, before depositing to the lending pool, we need to approve our ERC-20 WETH to be spent by the lending pool
    # Approve WETH for the lending protocol
    approve_erc20(AMOUNT_TO_DEPOSIT, lending_pool.address, erc20_address, account)
    # Deposit approved WETH
    # deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    # referralCode is depricated, so pass 0
    print(f"Depositing {erc20_address}")
    deposit_tx = lending_pool.deposit(
        erc20_address, AMOUNT_TO_DEPOSIT, account.address, 0, {"from": account}
    )
    deposit_tx.wait(1)
    print("The token has been deposited!")
    # now, we shall be able to borrow but the question is how much we can afford to borrow
    # getUserAccountData() will return all data across all the user's reserves
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow some DAI!")
    # first, we need DAI-ETH conversion rate to get DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # displaying the amount of DAI per 1 ETH by ( 1 / dai_eth_price )
    # then we multiply the amount of DAI in 1 ETH to the 95% of our total borrowable eth
    # we multiply by 0.95 as a buffer, to make sure or health factor is "better"
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now, we will borrow DAI
    # borrow(address asset, uint256 amount, uint256 interestRateMode, uint16 referralCode, address onBehalfOf)
    # inerestRateMode can be stable (1) or variale (2) - more on that at https://docs.aave.com/developers/v/2.0/the-core-protocol/lendingpool
    print(f"Borrowing {amount_dai_to_borrow} DAI")
    dai_token = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_token,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print(f"We have borrowed {amount_dai_to_borrow} DAI!\n")
    get_borrowable_data(lending_pool, account)
    # now, we are gonna repay what we borrowed
    repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)
    get_borrowable_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    # first, we need to approve repayng with DAI a.k.a approve DAI to the lending pool
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool.address,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    # repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("The debt has been repaid!")


def get_lending_pool():
    # the lending pool's address can change over time, so we have an Address Provider providing us with the actual address of the lending pool
    # ABI - ILendingPoolAddressesProvider
    # Address - config file
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    # now, we can get the actual lending pool's address
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI - ILendingPool
    # Address - above row of non-commented code
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print(f"Approving an ERC20 token: {erc20_address}")
    erc20 = interface.IERC20(erc20_address)
    # ABI
    # Address
    approval_tx = erc20.approve(spender, amount, {"from": account})
    approval_tx.wait(1)
    print(f"The ERC20 token has been approved!")
    return approval_tx


def get_borrowable_data(lending_pool, account):
    (
        total_collaterat_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        loan_to_value,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # the above values were returned in Wei, so we will turn them to ETH
    total_collaterat_eth = Web3.fromWei(total_collaterat_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    print(f"{total_collaterat_eth} worth of ETH has been deposited.")
    print(f"{total_debt_eth} worth of ETH has been borrowed.")
    print(f"{available_borrow_eth} worth of ETH can be borrowed.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    # fetching the 2nd element of the price data feed response to fetch the ETH price of DAI
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")
    return float(latest_price)


def main():
    borrow()
