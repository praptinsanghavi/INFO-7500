import React from "react";
import { useWallet } from "../contexts/WalletContext";

const ConnectWalletButton = () => {
  const { account, connectWallet } = useWallet();

  return (
    <div>
      {account ? (
        <p>🟢 Connected: {account.slice(0, 6)}...{account.slice(-4)}</p>
      ) : (
        <button onClick={connectWallet}>Connect Wallet</button>
      )}
    </div>
  );
};

export default ConnectWalletButton;
