// src/components/ui/NewsCard.jsx
import React, { useState } from "react";
import styles from "./NewsCard.module.css";

const NewsCard = ({ article }) => {
  const {
    title,
    link,
    summary = "Không có mô tả.",
    published_time,
    tickers = [],
    sectors = [],
  } = article;

  const [showFullSummary, setShowFullSummary] = useState(false);

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.source}>CafeF</span>
      </div>

      <a href={link} target="_blank" rel="noopener noreferrer" className={styles.title}>
        {title}
      </a>

      {/* Tag ticker */}
      {tickers.length > 0 && (
        <div className={styles.tickers}>
          {tickers.map((tk, index) =>
            typeof tk === "string" ? (
              <span key={index} className={styles.tickerTag}>
                {tk}
              </span>
            ) : (
              <span key={index} className={styles.tickerTag}>
                {tk.ticker} ({tk.sentiment?.toUpperCase?.() || "?"} - {(tk.confidence * 100).toFixed(1)}%)
              </span>
            )
          )}
        </div>
      )}

      {/* Tag sector */}
      {sectors.length > 0 && (
        <div className={styles.sectors}>
          {sectors.map((sector, index) =>
            typeof sector === "string" ? (
              <span key={index} className={styles.sectorTag}>
                {sector}
              </span>
            ) : (
              <span key={index} className={styles.sectorTag}>
                {sector.sector} ({sector.sentiment?.toUpperCase?.() || "?"} - {(sector.confidence * 100).toFixed(1)}%)
              </span>
            )
          )}
        </div>
      )}

      {/* Tóm tắt */}
      <p className={styles.summary}>
        {showFullSummary || summary.length < 300
          ? summary
          : summary.slice(0, 300) + "..."}
        {summary.length >= 300 && (
          <span
            onClick={() => setShowFullSummary(!showFullSummary)}
            style={{ color: "#1976d2", cursor: "pointer", marginLeft: "0.5rem" }}
          >
            {showFullSummary ? "Ẩn bớt" : "Xem thêm"}
          </span>
        )}
      </p>

      <div className={styles.footer}>
        <span className={styles.articleDate}>
          {new Date(published_time).toLocaleDateString("vi-VN")}
        </span>
      </div>
    </div>
  );
};

export default NewsCard;





