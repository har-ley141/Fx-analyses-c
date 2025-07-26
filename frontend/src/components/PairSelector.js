import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PairSelector = ({ value, onChange }) => {
  const [pairs, setPairs] = useState([]);

  useEffect(() => {
    const fetchPairs = async () => {
      try {
        const response = await axios.get(`${API}/fx/pairs`);
        setPairs(response.data.pairs);
      } catch (error) {
        console.error('Failed to fetch forex pairs:', error);
        // Fallback pairs
        setPairs([
          { symbol: "EURUSD=X", name: "EUR/USD", description: "Euro to US Dollar" },
          { symbol: "GBPUSD=X", name: "GBP/USD", description: "British Pound to US Dollar" },
          { symbol: "USDJPY=X", name: "USD/JPY", description: "US Dollar to Japanese Yen" },
          { symbol: "AUDUSD=X", name: "AUD/USD", description: "Australian Dollar to US Dollar" }
        ]);
      }
    };

    fetchPairs();
  }, []);

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm font-medium text-gray-700">Pair:</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[150px]"
      >
        {pairs.map(pair => (
          <option key={pair.symbol} value={pair.symbol}>
            {pair.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default PairSelector;