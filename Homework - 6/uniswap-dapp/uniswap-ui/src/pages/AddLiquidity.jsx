// src/pages/AddLiquidity.jsx
import { useState } from "react";
import { connectWallet, getRouterContract } from "../utils/contractUtils";
import { ethers } from "ethers";

const AddLiquidity = () => {
  const [amountA, setAmountA] = useState("");
  const [amountB, setAmountB] = useState("");
  const [message, setMessage] = useState("");

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;

  const handleAddLiquidity = async () => {
    setMessage("⏳ Processing...");

    try {
      const { signer } = await connectWallet();
      const router = getRouterContract(signer);

      const amountADesired = ethers.utils.parseUnits(amountA, 18);
      const amountBDesired = ethers.utils.parseUnits(amountB, 18);

      const ERC20_ABI = (await import("../abi/MockERC20.json")).default;

      const tokenAContract = new ethers.Contract(tokenA, ERC20_ABI, signer);
      const tokenBContract = new ethers.Contract(tokenB, ERC20_ABI, signer);

      await tokenAContract.approve(router.address, amountADesired);
      await tokenBContract.approve(router.address, amountBDesired);

      const deadline = Math.floor(Date.now() / 1000) + 60 * 10;

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
      setMessage("✅ Liquidity added successfully!");
    } catch (err) {
      console.error(err);
      setMessage("❌ Failed to add liquidity. Check console.");
    }
  };

  return (
    <div>
      <h2>Add Liquidity</h2>
      <input
        type="text"
        placeholder="Amount Token A"
        value={amountA}
        onChange={(e) => setAmountA(e.target.value)}
        style={{ marginRight: "1rem" }}
      />
      <input
        type="text"
        placeholder="Amount Token B"
        value={amountB}
        onChange={(e) => setAmountB(e.target.value)}
        style={{ marginRight: "1rem" }}
      />
      <button onClick={handleAddLiquidity}>Add Liquidity</button>
      <p style={{ marginTop: "1rem" }}>{message}</p>
    </div>
  );
};

export default AddLiquidity;
