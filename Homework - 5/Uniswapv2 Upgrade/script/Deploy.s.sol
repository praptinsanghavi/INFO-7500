// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/contracts/UniswapV2Factory.sol";
import "../src/contracts/UniswapV2Router02.sol";
import "../src/tests/mocks/MockERC20.sol";
import "../src/tests/mocks/MockWETH9.sol";


contract Deploy is Script {
    function run() external {
        vm.startBroadcast();

        // Deploy Token A and Token B
        MockERC20 tokenA = new MockERC20("TokenA", "TKA");
        MockERC20 tokenB = new MockERC20("TokenB", "TKB");

        // Deploy WETH
        // WETH9 weth = new WETH9();
        MockWETH9 weth = new MockWETH9();

        // Deploy Factory
        UniswapV2Factory factory = new UniswapV2Factory(msg.sender);

        // Deploy Router
        UniswapV2Router02 router = new UniswapV2Router02(address(factory), address(weth));

        // Print deployed addresses
        console.log("Token A:", address(tokenA));
        console.log("Token B:", address(tokenB));
        console.log("WETH:", address(weth));
        console.log("Factory:", address(factory));
        console.log("Router:", address(router));


        vm.stopBroadcast();
    }
}
