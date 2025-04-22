//SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "./DeployHelpers.s.sol";
import { DeployUniswapFactory } from "./DeployUniswapFactory.s.sol";

/**
 * @notice Main deployment script for all contracts
 * @dev Run this when you want to deploy multiple contracts at once
 *
 * Example: yarn deploy # runs this script(without`--file` flag)
 */
contract DeployScript is Script {
    function run() external {
        // Deploys all your contracts sequentially
        // Add new deployments here when needed

        DeployUniswapFactory deployFactory = new DeployUniswapFactory();
        deployFactory.run();

        // Deploy another contract
        // DeployMyContract myContract = new DeployMyContract();
        // myContract.run();
    }
}
