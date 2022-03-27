// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

// if we just need 1-2 functions of an interface, we can just re-write this interface

interface ILendingPoolAddressesProvider {
    function getLendingPool() external view returns (address);
}
