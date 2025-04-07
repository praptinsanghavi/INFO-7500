// src/pages/RemoveLiquidity.jsx
import { useState } from "react";
import { connectWallet, getRouterContract, getFactoryContract } from "../utils/contractUtils";
import { ethers } from "ethers";
import PairABI from "../abi/UniswapV2Pair.json"; // ABI for both Pair and LP tokens

const RemoveLiquidity = () => {
  const [lpAmount, setLpAmount] = useState("");
  const [message, setMessage] = useState("");

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;

  const removeLiquidity = async () => {
    try {
      setMessage("⏳ Connecting wallet and fetching contracts...");
      const { signer } = await connectWallet();

      const router = getRouterContract(signer);
      const factory = getFactoryContract(signer);

      setMessage("🔎 Getting pair address...");
      const pairAddress = await factory.getPair(tokenA, tokenB);

      if (pairAddress === ethers.constants.AddressZero) {
        setMessage("⚠️ Pair does not exist.");
        return;
      }

      const lpToken = new ethers.Contract(pairAddress, PairABI, signer);
      const amount = ethers.utils.parseUnits(lpAmount, 18);

      setMessage("🔐 Approving router to spend LP tokens...");
      const approval = await lpToken.approve(router.address, amount);
      await approval.wait();

      setMessage("💥 Removing liquidity...");
      const tx = await router.removeLiquidity(
        tokenA,
        tokenB,
        amount,
        0,
        0,
        await signer.getAddress(),
        Math.floor(Date.now() / 1000) + 60 * 10
      );
      await tx.wait();

      setMessage("✅ Liquidity removed successfully!");
    } catch (err) {
      console.error(err);
      setMessage("❌ Failed to remove liquidity.");
    }
  };

  return (
    <div>
      <h2>Remove Liquidity</h2>
      <input
        type="text"
        placeholder="LP Token Amount"
        value={lpAmount}
        onChange={(e) => setLpAmount(e.target.value)}
        style={{ marginRight: "1rem" }}
      />
      <button onClick={removeLiquidity}>Remove</button>
      <p>{message}</p>
    </div>
  );
};

export default RemoveLiquidity;
