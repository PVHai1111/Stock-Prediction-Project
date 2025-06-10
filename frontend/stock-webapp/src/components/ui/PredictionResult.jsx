/* frontend/stock-webapp/src/components/ui/PredictionResult.jsx */
import React from "react";
import styles from "./PredictionResult.module.css";
import NewsCard from "./NewsCard";

const PredictionResult = ({ result }) => {
  if (!result) return null;

  const {
    ticker,
    model,
    prediction,
    confidence,
    feature_importance,
    input_features,
    latest_close,
    date,
    latest_articles = [], // mặc định là [] nếu undefined
  } = result;

  const displayClose = typeof latest_close === "number" ? latest_close.toLocaleString() + " VND" : "N/A";
  const isUp = prediction === "Tăng";

  return (
    <div className={styles.container}>
      <h2>
        Kết quả dự đoán cho mã <span className={styles.ticker}>{ticker}</span>
      </h2>

      <div className={styles.summary}>
        <p><strong>Ngày:</strong> {date}</p>
        <p><strong>Mô hình:</strong> {model}</p>
        <p><strong>Giá đóng cửa gần nhất:</strong> {displayClose}</p>
        <p>
          <strong>Kết quả dự đoán:</strong>
          <span className={`${styles.prediction} ${isUp ? styles.up : styles.down}`}>
            {isUp ? "📈 Tăng" : "📉 Giảm"}
          </span>
        </p>
        <p><strong>Độ tin cậy:</strong> {(confidence * 100).toFixed(2)}%</p>
      </div>

      <div className={styles.section}>
        <h3>🎯 Đặc trưng đầu vào</h3>
        <ul>
          {Object.entries(input_features).map(([key, value]) => (
            <li key={key}><strong>{key}:</strong> {value}</li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3>📊 Độ quan trọng của đặc trưng</h3>
        <ul>
          {Object.entries(feature_importance).map(([feature, importance]) => (
            <li key={feature}>
              {feature}: {(importance * 100).toFixed(2)}%
            </li>
          ))}
        </ul>
      </div>

      {Array.isArray(latest_articles) && latest_articles.length > 0 && (
        <div className={styles.section}>
          <h3>📰 Tin tức liên quan gần nhất</h3>
          {latest_articles.map((article, index) => (
            <NewsCard key={index} article={article} />
          ))}
        </div>
      )}
    </div>
  );
};

export default PredictionResult;




