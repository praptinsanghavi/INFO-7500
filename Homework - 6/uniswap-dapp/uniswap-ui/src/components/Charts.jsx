// src/components/Charts.jsx

import { useEffect, useState } from "react";
import { ethers } from "ethers";
import { getFactoryContract } from "../utils/contractUtils";
import PairABI from "../abi/UniswapV2Pair.json";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";

// ✅ Import the Constant Product Curve chart component
import ConstantProductCurve from "./ConstantProductCurve";

/**
 * Charts.jsx
 * 
 * This component displays three real-time charts:
 * 1. 📐 Constant Product Curve: Shows the hyperbolic x * y = k using current reserves.
 * 2. 📉 Reserves Curve: Tracks real-time reserves of Token A & B.
 * 3. 📈 Execution Price Chart: Displays Token B per Token A pricing per swap.
 * 
 * @param {object} signer - The connected wallet signer (from ethers.js)
 */

const Charts = ({ signer }) => {
  const [reserveChartData, setReserveChartData] = useState([]);
  const [priceChartData, setPriceChartData] = useState([]);

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;
  const factoryAddress = import.meta.env.VITE_FACTORY_ADDRESS;

  useEffect(() => {
    if (!signer) return;

    let pair;

    const setupListeners = async () => {
      try {
        const factory = getFactoryContract(signer);
        const pairAddress = await factory.getPair(tokenA, tokenB);
        if (pairAddress === ethers.constants.AddressZero) return;

        pair = new ethers.Contract(pairAddress, PairABI, signer);

        /**
         * Updates reserve chart with new Sync event data
         */
        const updateReserves = (reserve0Raw, reserve1Raw) => {
          const reserve0 = parseFloat(ethers.utils.formatUnits(reserve0Raw, 18));
          const reserve1 = parseFloat(ethers.utils.formatUnits(reserve1Raw, 18));

          const point = {
            time: new Date().toLocaleTimeString(),
            reserve0,
            reserve1,
          };

          setReserveChartData((prev) => [...prev.slice(-9), point]);
        };

        /**
         * Updates price chart with new Swap event data
         */
        const updateSwapPrice = (amount0In, amount1In, amount0Out, amount1Out) => {
          let price = 0;

          if (amount0In.gt(0)) {
            price =
              parseFloat(ethers.utils.formatUnits(amount1Out, 18)) /
              parseFloat(ethers.utils.formatUnits(amount0In, 18));
          } else if (amount1In.gt(0)) {
            price =
              parseFloat(ethers.utils.formatUnits(amount1In, 18)) /
              parseFloat(ethers.utils.formatUnits(amount0Out, 18));
          }

          const point = {
            time: new Date().toLocaleTimeString(),
            price: Number(price.toFixed(6)),
          };

          setPriceChartData((prev) => [...prev.slice(-9), point]);
        };

        // Fetch initial reserves
        const [initialReserve0, initialReserve1] = await pair.getReserves();
        updateReserves(initialReserve0, initialReserve1);

        // Listen to Sync events
        pair.on("Sync", (reserve0, reserve1) => {
          updateReserves(reserve0, reserve1);
        });

        // Listen to Swap events
        pair.on(
          "Swap",
          (sender, amount0In, amount1In, amount0Out, amount1Out, to) => {
            updateSwapPrice(amount0In, amount1In, amount0Out, amount1Out);
          }
        );
      } catch (err) {
        console.error("Error setting up chart listeners:", err);
      }
    };

    setupListeners();

    // Cleanup listeners on unmount
    return () => {
      if (pair) {
        pair.removeAllListeners("Sync");
        pair.removeAllListeners("Swap");
      }
    };
  }, [signer]);

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "2rem", justifyContent: "center" }}>
      {/* 📐 Constant Product Curve (x * y = k) */}
      <ConstantProductCurve signer={signer} />

      {/* 📉 Real-time Reserves Curve Chart */}
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "1rem",
          backgroundColor: "#fafafa",
        }}
      >
        <h3>📉 Reserves Curve (Token A & B)</h3>
        <LineChart width={500} height={300} data={reserveChartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="reserve0" stroke="#8884d8" name="Reserve A" />
          <Line type="monotone" dataKey="reserve1" stroke="#82ca9d" name="Reserve B" />
        </LineChart>
      </div>

      {/* 📈 Real-time Execution Price Chart */}
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "1rem",
          backgroundColor: "#fafafa",
        }}
      >
        <h3>📈 Price Distribution (Token B / A)</h3>
        <LineChart width={500} height={300} data={priceChartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="price" stroke="#ff7300" name="Price (B per A)" />
        </LineChart>
      </div>
    </div>
  );
};

export default Charts;
