// src/components/ui/StockInput.jsx

import React, { useState, useEffect } from "react";
import styles from "./StockInput.module.css";

const DEFAULT_TICKERS = [
];

const StockInput = ({ value, onChange, placeholder = "Nhập mã cổ phiếu..." }) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [tickers, setTickers] = useState([]);

  useEffect(() => {
    // TODO: Nếu sau này có API riêng để fetch list mã cổ phiếu, dùng ở đây
    setTickers(DEFAULT_TICKERS);
  }, []);

  useEffect(() => {
    if (query.trim() === "") {
      setSuggestions([]);
    } else {
      const lower = query.toLowerCase();
      const filtered = tickers.filter(ticker => ticker.toLowerCase().startsWith(lower));
      setSuggestions(filtered);
    }
  }, [query, tickers]);

  const handleSelect = (ticker) => {
    setQuery(ticker);
    onChange(ticker);
    setSuggestions([]);
  };

  return (
    <div className={styles.container}>
      <input
        className={styles.input}
        type="text"
        value={query}
        placeholder={placeholder}
        onChange={(e) => {
          setQuery(e.target.value.toUpperCase());
          onChange(e.target.value.toUpperCase());
        }}
        onFocus={() => {
          if (query) {
            const filtered = tickers.filter(ticker =>
              ticker.toLowerCase().startsWith(query.toLowerCase())
            );
            setSuggestions(filtered);
          }
        }}
      />
      {suggestions.length > 0 && (
        <ul className={styles.suggestions}>
          {suggestions.map((s) => (
            <li key={s} onClick={() => handleSelect(s)}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default StockInput;
