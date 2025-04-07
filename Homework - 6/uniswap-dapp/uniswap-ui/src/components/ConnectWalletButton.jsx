import React, { useEffect } from "react";
import { useWallet } from "../contexts/WalletContext";

const ConnectWalletButton = ({ onConnect }) => {
  const { account, connectWallet, signer } = useWallet();

  const handleClick = async () => {
    await connectWallet();
    if (onConnect && signer) {
      onConnect(signer); // ✅ Notify parent component like App.jsx
    }
  };

  // Optional: call onConnect automatically when signer changes
  useEffect(() => {
    if (onConnect && signer) {
      onConnect(signer);
    }
  }, [signer]);

  return (
    <div>
      {account ? (
        <p>🟢 Connected: {account.slice(0, 6)}...{account.slice(-4)}</p>
      ) : (
        <button onClick={handleClick}>Connect Wallet</button>
      )}
    </div>
  );
};

export default ConnectWalletButton;
