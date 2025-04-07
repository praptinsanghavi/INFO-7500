// src/components/ExecutionPriceChart.jsx
import { useEffect, useState } from "react";
import { ethers } from "ethers";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";
import PairABI from "../abi/UniswapV2Pair.json";

const ExecutionPriceChart = ({ signer }) => {
  const [priceData, setPriceData] = useState([]);
  const [pairContract, setPairContract] = useState(null);

  const tokenA = import.meta.env.VITE_TOKEN_A;
  const tokenB = import.meta.env.VITE_TOKEN_B;
  const factoryAddress = import.meta.env.VITE_FACTORY_ADDRESS;

  // Load historical prices
  useEffect(() => {
    const fetchPrices = async () => {
      if (!signer) return;

      try {
        const factory = new ethers.Contract(factoryAddress, PairABI, signer);
        const pairAddress = await factory.getPair(tokenA, tokenB);
        if (!pairAddress || pairAddress === ethers.constants.AddressZero) return;

        const pair = new ethers.Contract(pairAddress, PairABI, signer);
        setPairContract(pair);

        const currentBlock = await signer.provider.getBlockNumber();
        const events = await pair.queryFilter("Swap", currentBlock - 5000, currentBlock);

        const parsedPrices = events.map((event, idx) => {
          const { amount0In, amount1In, amount0Out, amount1Out } = event.args;

          let price = 0;
          if (amount0In.gt(0)) {
            price = parseFloat(ethers.utils.formatUnits(amount1Out, 18)) /
                    parseFloat(ethers.utils.formatUnits(amount0In, 18));
          } else if (amount1In.gt(0)) {
            price = parseFloat(ethers.utils.formatUnits(amount1In, 18)) /
                    parseFloat(ethers.utils.formatUnits(amount0Out, 18));
          }

          return {
            index: idx + 1,
            price: Number(price.toFixed(6)),
          };
        });

        setPriceData(parsedPrices);
      } catch (error) {
        console.error("Failed to fetch swap data:", error);
      }
    };

    fetchPrices();
  }, [signer]);

  // Real-time listener
  useEffect(() => {
    if (!pairContract) return;

    const onSwap = (sender, amount0In, amount1In, amount0Out, amount1Out) => {
      let price = 0;
      if (amount0In.gt(0)) {
        price = parseFloat(ethers.utils.formatUnits(amount1Out, 18)) /
                parseFloat(ethers.utils.formatUnits(amount0In, 18));
      } else if (amount1In.gt(0)) {
        price = parseFloat(ethers.utils.formatUnits(amount1In, 18)) /
                parseFloat(ethers.utils.formatUnits(amount0Out, 18));
      }

      setPriceData(prev => [
        ...prev,
        {
          index: prev.length + 1,
          price: Number(price.toFixed(6)),
        }
      ]);
    };

    pairContract.on("Swap", onSwap);

    return () => {
      pairContract.off("Swap", onSwap);
    };
  }, [pairContract]);

  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "8px",
        padding: "1rem",
        width: "100%",
        maxWidth: "600px",
        backgroundColor: "#fafafa",
        marginTop: "2rem",
      }}
    >
      <h2
        style={{
          marginBottom: "1rem",
          fontSize: "1.25rem",
          color: "#333",
          fontWeight: "bold",
        }}
      >
        📉 Execution Price Per Swap (Token B per Token A)
      </h2>

      <LineChart width={550} height={300} data={priceData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="index"
          label={{ value: "Swap #", position: "insideBottomRight", offset: -5 }}
        />
        <YAxis
          label={{ value: "Price", angle: -90, position: "insideLeft" }}
        />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="price" stroke="#0070f3" />
      </LineChart>
    </div>
  );
};

export default ExecutionPriceChart;
