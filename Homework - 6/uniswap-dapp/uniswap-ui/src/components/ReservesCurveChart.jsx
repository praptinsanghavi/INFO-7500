// src/components/ReservesCurveChart.jsx
import { useEffect, useState } from "react";
import { ethers } from "ethers";
import { getFactoryContract } from "../utils/contractUtils";
import PairABI from "../abi/UniswapV2Pair.json";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

const ReservesCurveChart = ({ signer }) => {
  const [chartData, setChartData] = useState([]);
  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;

  useEffect(() => {
    if (!signer) return;

    let pair;

    const fetchAndSubscribe = async () => {
      const factory = getFactoryContract(signer);
      const pairAddress = await factory.getPair(tokenA, tokenB);
      if (pairAddress === ethers.constants.AddressZero) return;

      pair = new ethers.Contract(pairAddress, PairABI, signer);

      const updateChart = (reserve0Raw, reserve1Raw) => {
        const reserve0 = parseFloat(ethers.utils.formatUnits(reserve0Raw, 18));
        const reserve1 = parseFloat(ethers.utils.formatUnits(reserve1Raw, 18));
        const price = reserve1 / reserve0;

        const point = {
          time: new Date().toLocaleTimeString(),
          reserve0,
          reserve1,
          price,
        };

        setChartData((prev) => [...prev.slice(-9), point]);
      };

      const [initialReserve0, initialReserve1] = await pair.getReserves();
      updateChart(initialReserve0, initialReserve1);

      pair.on("Sync", (r0, r1) => updateChart(r0, r1));
    };

    fetchAndSubscribe();

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
      <h3>📉 Reserves Curve (Token A & B)</h3>
      <LineChart width={500} height={300} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="reserve0" stroke="#8884d8" name="Reserve A" />
        <Line type="monotone" dataKey="reserve1" stroke="#82ca9d" name="Reserve B" />
      </LineChart>
    </div>
  );
};

export default ReservesCurveChart;
