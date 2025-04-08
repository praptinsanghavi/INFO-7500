// 📁 File: src/components/ConstantProductCurve.jsx

import { useEffect, useState } from "react";
import { ethers } from "ethers";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { getFactoryContract } from "../utils/contractUtils";
import PairABI from "../abi/UniswapV2Pair.json";

/**
 * 📉 ConstantProductCurve
 * This component visualizes the Uniswap x*y = k curve.
 * It fetches the current reserves, calculates the constant k,
 * and plots the curve along with a red dot for current reserves.
 *
 * Props:
 * - signer: Ethers.js signer from connected wallet
 */
const ConstantProductCurve = ({ signer }) => {
  const [curveData, setCurveData] = useState([]);
  const [currentPoint, setCurrentPoint] = useState(null);

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;
  const factoryAddress = import.meta.env.VITE_FACTORY_ADDRESS;

  useEffect(() => {
    if (!signer) return;

    let pair;

    const fetchAndPlotCurve = async () => {
      try {
        const factory = getFactoryContract(signer);
        const pairAddress = await factory.getPair(tokenA, tokenB);
        if (pairAddress === ethers.constants.AddressZero) return;

        pair = new ethers.Contract(pairAddress, PairABI, signer);

        const [reserve0Raw, reserve1Raw] = await pair.getReserves();

        const x = parseFloat(ethers.utils.formatUnits(reserve0Raw, 18));
        const y = parseFloat(ethers.utils.formatUnits(reserve1Raw, 18));
        const k = x * y;

        const points = [];
        const steps = 100;
        const xMin = x * 0.2;
        const xMax = x * 2;
        const step = (xMax - xMin) / steps;

        for (let xi = xMin; xi <= xMax; xi += step) {
          const yi = k / xi;
          points.push({ x: parseFloat(xi.toFixed(4)), y: parseFloat(yi.toFixed(4)) });
        }

        setCurveData(points);
        setCurrentPoint({ x: parseFloat(x.toFixed(4)), y: parseFloat(y.toFixed(4)) });

        // Subscribe to Sync for real-time updates
        pair.on("Sync", (reserve0, reserve1) => {
          const newX = parseFloat(ethers.utils.formatUnits(reserve0, 18));
          const newY = parseFloat(ethers.utils.formatUnits(reserve1, 18));
          const newK = newX * newY;

          const newPoints = [];
          for (let xi = newX * 0.2; xi <= newX * 2; xi += step) {
            const yi = newK / xi;
            newPoints.push({ x: parseFloat(xi.toFixed(4)), y: parseFloat(yi.toFixed(4)) });
          }

          setCurveData(newPoints);
          setCurrentPoint({ x: parseFloat(newX.toFixed(4)), y: parseFloat(newY.toFixed(4)) });
        });
      } catch (err) {
        console.error("Failed to fetch curve data:", err);
      }
    };

    fetchAndPlotCurve();

    return () => {
      if (pair) pair.removeAllListeners("Sync");
    };
  }, [signer]);

  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "8px",
        padding: "1rem",
        backgroundColor: "#fafafa",
      }}
    >
      <h3 style={{ marginBottom: "1rem" }}>🧮 Constant Product Curve (x * y = k)</h3>
      <ScatterChart width={500} height={300}>
        <CartesianGrid />
        <XAxis type="number" dataKey="x" name="Token A Reserve" />
        <YAxis type="number" dataKey="y" name="Token B Reserve" />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        <Legend />
        <Scatter name="x*y = k" data={curveData} fill="#8884d8" line />
        {currentPoint && (
          <Scatter name="Current Reserves" data={[currentPoint]} fill="#ff0000" />
        )}
      </ScatterChart>
    </div>
  );
};

export default ConstantProductCurve;
