/* frontend/stock-webapp/src/components/ui/PriceTable.jsx */
import React from "react";
import styles from "./PriceTable.module.css";

export default function PriceTable({ data }) {
  if (!data.length) return <p>Không có dữ liệu.</p>;

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Ngày</th>
          <th>Open</th>
          <th>High</th>
          <th>Low</th>
          <th>Close</th>
          <th>Volume</th>
          <th>GTGD</th>
          <th>Positive</th>
          <th>Neutral</th>
          <th>Negative</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            <td>{row.date}</td>
            <td>{row.open}</td>
            <td>{row.high}</td>
            <td>{row.low}</td>
            <td>{row.close}</td>
            <td>{row.volume.toLocaleString()}</td>
            <td>{row.value.toLocaleString()}</td>
            <td>{row.positive_articles}</td>
            <td>{row.neutral_articles}</td>
            <td>{row.negative_articles}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
