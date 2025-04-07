// src/pages/Swap.jsx
import { useState } from "react";
import { connectWallet, getRouterContract } from "../utils/contractUtils";
import { ethers } from "ethers";
import ERC20ABI from "../abi/MockERC20.json";

const Swap = () => {
  const [amountIn, setAmountIn] = useState("");
  const [message, setMessage] = useState("");

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;

  const handleSwap = async () => {
    try {
      setMessage("⏳ Connecting wallet...");
      const { signer } = await connectWallet();
      const router = getRouterContract(signer);
      const account = await signer.getAddress();

      if (!amountIn || isNaN(amountIn)) {
        setMessage("⚠️ Enter a valid amount.");
        return;
      }

      const amountInParsed = ethers.utils.parseUnits(amountIn, 18);

      // Step 1: Estimate amountOut using getAmountsOut
      const amountsOut = await router.getAmountsOut(amountInParsed, [tokenA, tokenB]);
      const estimatedAmountOut = amountsOut[1];

      // Step 2: Apply slippage buffer (0.5%)
      const slippageTolerance = 0.005; // 0.5%
      const slippageAmount = estimatedAmountOut.mul(Math.floor(slippageTolerance * 1000)).div(1000);
      const minAmountOut = estimatedAmountOut.sub(slippageAmount);

      // Step 3: Approve router to spend tokenA
      const tokenAContract = new ethers.Contract(tokenA, ERC20ABI, signer);
      setMessage("🔐 Approving token A for swap...");
      const approvalTx = await tokenAContract.approve(router.address, amountInParsed);
      await approvalTx.wait();

      // Step 4: Perform the swap
      setMessage("💱 Swapping tokens...");
      const tx = await router.swapExactTokensForTokens(
        amountInParsed,
        minAmountOut,
        [tokenA, tokenB],
        account,
        Math.floor(Date.now() / 1000) + 60 * 10 // deadline = 10 mins from now
      );

      await tx.wait();
      setMessage(`✅ Swap complete! Min received: ${ethers.utils.formatUnits(minAmountOut, 18)} Token B`);
    } catch (error) {
      console.error("Swap error:", error);
      setMessage("❌ Swap failed. Check console for details.");
    }
  };

  return (
    <div>
      <h2>Swap Token A → Token B</h2>
      <input
        type="text"
        placeholder="Amount Token A"
        value={amountIn}
        onChange={(e) => setAmountIn(e.target.value)}
        style={{ marginRight: "1rem" }}
      />
      <button onClick={handleSwap}>Swap</button>
      <p>{message}</p>
    </div>
  );
};

export default Swap;
