// src/utils/contractUtils.js

import { ethers } from "ethers";
import FactoryABI from "../abi/UniswapV2Factory.json";
import RouterABI from "../abi/UniswapV2Router02.json";
import PairABI from "../abi/UniswapV2Pair.json";
import MockERC20ABI from "../abi/MockERC20.json"; // 👈 needed for approve()

export const connectWallet = async () => {
  const provider = new ethers.providers.Web3Provider(window.ethereum);
  await provider.send("eth_requestAccounts", []);
  const signer = provider.getSigner();
  return { provider, signer };
};

export const getFactoryContract = (signer) =>
  new ethers.Contract(import.meta.env.VITE_UNISWAP_FACTORY, FactoryABI, signer);

export const getRouterContract = (signer) =>
  new ethers.Contract(import.meta.env.VITE_UNISWAP_ROUTER, RouterABI, signer);

export const getPairContract = (address, signer) =>
  new ethers.Contract(address, PairABI, signer);

// 👇 ADD THIS FUNCTION BELOW
export const addLiquidity = async (signer, tokenA, tokenB, amountADesired, amountBDesired) => {
  const router = getRouterContract(signer);

  const tokenAContract = new ethers.Contract(tokenA, MockERC20ABI, signer);
  const tokenBContract = new ethers.Contract(tokenB, MockERC20ABI, signer);

  // Approve router to spend tokens
  const approvalA = await tokenAContract.approve(router.address, amountADesired);
  await approvalA.wait();

  const approvalB = await tokenBContract.approve(router.address, amountBDesired);
  await approvalB.wait();

  const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20 mins from now

  const tx = await router.addLiquidity(
    tokenA,
    tokenB,
    amountADesired,
    amountBDesired,
    0,
    0,
    await signer.getAddress(),
    deadline
  );

  await tx.wait();
  return tx;
};