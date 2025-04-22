// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "contracts/core/interfaces/IUniswapV2Pair.sol";
import "contracts/core/interfaces/IUniswapV2Factory.sol";
import "contracts/libraries/Babylonian.sol";
import "contracts/libraries/FullMath.sol";

import "./UniswapV2Library.sol";

// library containing some math for dealing with the liquidity shares of a pair, e.g. computing their exact value
// in terms of the underlying tokens
library UniswapV2LiquidityMathLibrary {
    // computes the direction and magnitude of the profit-maximizing trade
    function computeProfitMaximizingTrade(
        uint256 truePriceTokenA,
        uint256 truePriceTokenB,
        uint256 reserveA,
        uint256 reserveB
    ) internal pure returns (bool aToB, uint256 amountIn) {
        // Compare ratio of (reserveA * truePriceTokenB / reserveB) with truePriceTokenA
        aToB = FullMath.mulDiv(reserveA, truePriceTokenB, reserveB) < truePriceTokenA;

        // replaced .mul() with *
        uint256 invariant = reserveA * reserveB;

        // Next lines: replaced .mul(...) with *
        uint256 leftSide = Babylonian.sqrt(
            FullMath.mulDiv(
                invariant * 1000,
                (aToB ? truePriceTokenA : truePriceTokenB),
                (aToB ? truePriceTokenB : truePriceTokenA) * 997
            )
        );
        uint256 rightSide = (aToB ? (reserveA * 1000) : (reserveB * 1000)) / 997;

        if (leftSide < rightSide) return (false, 0);

        // replaced .sub(...) with -
        amountIn = leftSide - rightSide;
    }

    // gets the reserves after an arbitrage moves the price to the profit-maximizing ratio given an externally observed true price
    function getReservesAfterArbitrage(
        address factory,
        address tokenA,
        address tokenB,
        uint256 truePriceTokenA,
        uint256 truePriceTokenB
    ) internal view returns (uint256 reserveA, uint256 reserveB) {
        // first get reserves before the swap
        (reserveA, reserveB) = UniswapV2Library.getReserves(factory, tokenA, tokenB);
        require(reserveA > 0 && reserveB > 0, "UniswapV2ArbitrageLibrary: ZERO_PAIR_RESERVES");

        // then compute how much to swap to arb to the true price
        (bool aToB, uint256 amountIn) = computeProfitMaximizingTrade(
            truePriceTokenA,
            truePriceTokenB,
            reserveA,
            reserveB
        );

        if (amountIn == 0) {
            return (reserveA, reserveB);
        }

        // now affect the trade to the reserves
        if (aToB) {
            uint amountOut = UniswapV2Library.getAmountOut(amountIn, reserveA, reserveB);
            reserveA += amountIn;
            reserveB -= amountOut;
        } else {
            uint amountOut = UniswapV2Library.getAmountOut(amountIn, reserveB, reserveA);
            reserveB += amountIn;
            reserveA -= amountOut;
        }
    }

    // computes liquidity value given all the parameters of the pair
    function computeLiquidityValue(
        uint256 reservesA,
        uint256 reservesB,
        uint256 totalSupply,
        uint256 liquidityAmount,
        bool feeOn,
        uint kLast
    ) internal pure returns (uint256 tokenAAmount, uint256 tokenBAmount) {
        if (feeOn && kLast > 0) {
            // replaced .mul() with *
            uint rootK = Babylonian.sqrt(reservesA * reservesB);
            uint rootKLast = Babylonian.sqrt(kLast);
            if (rootK > rootKLast) {
                uint numerator1 = totalSupply;
                // replaced .sub() with -
                uint numerator2 = rootK - rootKLast;
                // replaced .mul() and .add() with * and +
                uint denominator = (rootK * 5) + rootKLast;
                uint feeLiquidity = FullMath.mulDiv(numerator1, numerator2, denominator);
                // replaced .add() with +
                totalSupply = totalSupply + feeLiquidity;
            }
        }
        // final returns: replaced .mul(...) with * and used normal division
        tokenAAmount = (reservesA * liquidityAmount) / totalSupply;
        tokenBAmount = (reservesB * liquidityAmount) / totalSupply;
    }

    // get all current parameters from the pair and compute value of a liquidity amount
    // **note this is subject to manipulation, e.g. sandwich attacks**. prefer passing a manipulation resistant price to
    // #getLiquidityValueAfterArbitrageToPrice
    function getLiquidityValue(
        address factory,
        address tokenA,
        address tokenB,
        uint256 liquidityAmount
    ) internal view returns (uint256 tokenAAmount, uint256 tokenBAmount) {
        (uint256 reservesA, uint256 reservesB) = UniswapV2Library.getReserves(factory, tokenA, tokenB);
        IUniswapV2Pair pair = IUniswapV2Pair(UniswapV2Library.pairFor(factory, tokenA, tokenB));
        bool feeOn = IUniswapV2Factory(factory).feeTo() != address(0);
        uint kLast = feeOn ? pair.kLast() : 0;
        uint totalSupply = pair.totalSupply();
        return computeLiquidityValue(reservesA, reservesB, totalSupply, liquidityAmount, feeOn, kLast);
    }

    // given two tokens, tokenA and tokenB, and their "true price", i.e. the observed ratio of value of token A to token B,
    // and a liquidity amount, returns the value of the liquidity in terms of tokenA and tokenB
    function getLiquidityValueAfterArbitrageToPrice(
        address factory,
        address tokenA,
        address tokenB,
        uint256 truePriceTokenA,
        uint256 truePriceTokenB,
        uint256 liquidityAmount
    ) internal view returns (uint256 tokenAAmount, uint256 tokenBAmount) {
        bool feeOn = IUniswapV2Factory(factory).feeTo() != address(0);
        IUniswapV2Pair pair = IUniswapV2Pair(UniswapV2Library.pairFor(factory, tokenA, tokenB));
        uint kLast = feeOn ? pair.kLast() : 0;
        uint totalSupply = pair.totalSupply();

        // this also checks that totalSupply > 0
        require(totalSupply >= liquidityAmount && liquidityAmount > 0, "ComputeLiquidityValue: LIQUIDITY_AMOUNT");

        (uint reservesA, uint reservesB) = getReservesAfterArbitrage(
            factory,
            tokenA,
            tokenB,
            truePriceTokenA,
            truePriceTokenB
        );

        return computeLiquidityValue(reservesA, reservesB, totalSupply, liquidityAmount, feeOn, kLast);
    }
}
