// src/components/PoolInfoCard.jsx
import { useEffect, useState } from "react";
import { getFactoryContract, connectWallet } from "../utils/contractUtils";
import PairABI from "../abi/UniswapV2Pair.json";
import { ethers } from "ethers";
import { Link } from "react-router-dom"; // ✅ Added

const PoolInfoCard = () => {
  const [signer, setSigner] = useState(null);
  const [walletAddress, setWalletAddress] = useState("");
  const [pairAddress, setPairAddress] = useState("");
  const [reserves, setReserves] = useState(null);

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;

  const connect = async () => {
    const { signer } = await connectWallet();
    const address = await signer.getAddress();
    setSigner(signer);
    setWalletAddress(address);
  };

  const fetchPoolData = async () => {
    if (!signer) return;

    const factory = getFactoryContract(signer);
    const pair = await factory.getPair(tokenA, tokenB);
    setPairAddress(pair);

    if (pair === ethers.constants.AddressZero) {
      setReserves(null);
      return;
    }

    const pairContract = new ethers.Contract(pair, PairABI, signer);
    const [reserve0, reserve1] = await pairContract.getReserves();

    setReserves({
      reserve0: reserve0.toString(),
      reserve1: reserve1.toString()
    });
  };

  useEffect(() => {
    if (signer) {
      fetchPoolData();
    }
  }, [signer]);

  return (
    <div style={{ border: "1px solid #eee", padding: "1rem", marginTop: "2rem" }}>
      <h2>🧪 Pool Info</h2>
      {!signer ? (
        <button onClick={connect}>🔌 Connect Wallet</button>
      ) : (
        <>
          <p><strong>Wallet:</strong> {walletAddress}</p>
          <p><strong>Token A:</strong> {tokenA}</p>
          <p><strong>Token B:</strong> {tokenB}</p>
          <p><strong>Pair Address:</strong> {pairAddress || "Loading..."}</p>
          {reserves && (
            <>
              <p><strong>Reserve 0:</strong> {reserves.reserve0}</p>
              <p><strong>Reserve 1:</strong> {reserves.reserve1}</p>
            </>
          )}
          <Link to="/add-liquidity">
            <button style={{ marginTop: "1rem" }}>➕ Add Liquidity</button>
          </Link>
        </>
      )}
    </div>
  );
};

export default PoolInfoCard;
