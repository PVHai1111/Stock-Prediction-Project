// frontend/stock-webapp/src/pages/PriceHistoryPage/index.jsx
import React, { useState } from "react";
import StockInput from "../../components/ui/StockInput";
import PriceChart from "../../components/ui/PriceChart";
import styles from "./PriceHistoryPage.module.css";
import { getPriceHistory, updatePrice } from "../../services/api";
import PriceTable from "../../components/ui/PriceTable";
import { exportPriceCSV } from "../../services/api";


export default function PriceHistoryPage() {
  const [ticker, setTicker] = useState("");
  const [priceData, setPriceData] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const handleExport = async () => {
    try {
      if (!ticker) return;
      await exportPriceCSV(ticker, startDate, endDate);
    } catch (err) {
      console.error("Lỗi export CSV:", err);
      alert("Xuất file CSV thất bại.");
    }
  };


  const handleSearch = async () => {
    if (!ticker) return;
    try {
      setPriceData([]); // Clear dữ liệu cũ
      await updatePrice(ticker);
      const data = await getPriceHistory(ticker, startDate, endDate);
      setPriceData(data);
    } catch (err) {
      console.error("Lỗi khi cập nhật dữ liệu giá:", err);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Lịch sử giá cổ phiếu</h1>
      <div className={styles.topControls}>
        <StockInput value={ticker} onChange={setTicker} />
        <label>
          Từ ngày:
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        </label>
        <label>
          Đến ngày:
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        </label>
        <button className={styles.button} onClick={handleSearch}>Lọc</button>
        <button className={styles.button} onClick={handleExport}>Export CSV</button>
      </div>
      <div className={styles.chartContainer}>
        <PriceChart data={priceData} />
        <h2 style={{ marginTop: "30px" }}>Chi tiết lịch sử giá & bài viết</h2>
        <PriceTable data={priceData.slice().reverse()} />
      </div>
    </div>
  );
}












