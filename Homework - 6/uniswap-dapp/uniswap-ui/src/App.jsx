// src/App.jsx
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ConnectWalletButton from "./components/ConnectWalletButton.jsx";
import PoolInfoCard from "./components/PoolInfoCard.jsx";
import AddLiquidity from "./pages/AddLiquidity.jsx";
import RemoveLiquidity from "./pages/RemoveLiquidity.jsx"; // ✅ new import
import Swap from "./pages/Swap.jsx"; // ✅ new import
import Charts from "./components/Charts"; // ✅ existing chart component
import ExecutionPriceChart from "./components/ExecutionPriceChart.jsx"; // ✅ new import
import { connectWallet } from "./utils/contractUtils"; // ✅ to connect and get signer

function App() {
  const [signer, setSigner] = useState(null);

  const handleConnectWallet = async () => {
    const { signer } = await connectWallet();
    setSigner(signer);
  };

  console.log("App.jsx loaded 🚀");

  return (
    <Router>
      <div style={{ padding: "2rem", fontFamily: "Arial" }}>
        <h1>🦄 Uniswap v2 Web3 UI</h1>
        <ConnectWalletButton onConnect={handleConnectWallet} />

        {/* ✅ Navigation buttons */}
        <nav style={{ marginTop: "1rem", marginBottom: "1rem" }}>
          <Link to="/">
            <button style={{ marginRight: "1rem" }}>🏠 Home</button>
          </Link>
          <Link to="/add-liquidity">
            <button style={{ marginRight: "1rem" }}>➕ Add Liquidity</button>
          </Link>
          <Link to="/remove-liquidity">
            <button style={{ marginRight: "1rem" }}>➖ Remove Liquidity</button>
          </Link>
          <Link to="/swap">
            <button style={{ marginRight: "1rem" }}>🔁 Swap</button>
          </Link>
          <Link to="/charts">
            <button>📊 Charts</button>
          </Link>
        </nav>

        {/* ✅ Page Routes */}
        <Routes>
          <Route path="/" element={<PoolInfoCard />} />
          <Route path="/add-liquidity" element={<AddLiquidity />} />
          <Route path="/remove-liquidity" element={<RemoveLiquidity />} />
          <Route path="/swap" element={<Swap />} />
          <Route
            path="/charts"
            element={
              <div style={{ display: "flex", flexWrap: "wrap", gap: "2rem" }}>
                <Charts signer={signer} />
                <ExecutionPriceChart signer={signer} />
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
