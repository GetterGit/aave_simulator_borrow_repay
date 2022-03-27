1. Swap ETH to WETH
1. Deposit the resulting  WETH to Aave
2. Borrow some asset with the ETH collateral
3. Extra - Sell the borrowed asset (short selling)
4. Repay everything back

The logic of working with Aave within this codebase is similar to how to work with DEXes like Paraswap, Uniswap etc.

Testing:
Integration test: Rinkeby
Unit tests: Mainnet-fork since we don't need to deploy any mocks

Aave mechanics notes:
1. When we deposit funds (e.g. ETH), Aave swaps ETH for WETH (ERC-20 version of ETH) using the WETHGateway contract. Then, resulting WETH is stored in the Aave protocol
