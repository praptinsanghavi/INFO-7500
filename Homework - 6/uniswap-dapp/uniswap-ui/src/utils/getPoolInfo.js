import { ethers } from "ethers";
import PairABI from "../abi/UniswapV2Pair.json";

export const getPoolInfo = async (factory, tokenA, tokenB, signer) => {
  const pairAddress = await factory.getPair(tokenA, tokenB);
  if (pairAddress === ethers.constants.AddressZero) {
    return null;
  }

  const pairContract = new ethers.Contract(pairAddress, PairABI, signer);
  const [reserve0, reserve1] = await pairContract.getReserves();

  const token0 = await pairContract.token0();
  const token1 = await pairContract.token1();

  return {
    pairAddress,
    token0,
    token1,
    reserve0: reserve0.toString(),
    reserve1: reserve1.toString()
  };
};
