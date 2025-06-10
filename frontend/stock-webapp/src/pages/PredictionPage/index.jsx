// src/pages/PredictionPage/index.jsx
import React, { useState } from "react";
import styles from "./PredictionPage.module.css";
import { predictStock } from "../../services/api";
import PredictionResult from "../../components/ui/PredictionResult";

const modelOptions = ["random_forest", "xgboost", "lightgbm"];
const tickerOptions = [
  "FPT", "VHM", "HPG", "SSI", "MWG", "SHS", "MBS", "HCM", "MBB", "VIC"
];

const PredictionPage = () => {
  const [ticker, setTicker] = useState("");
  const [model, setModel] = useState("random_forest");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progressMessage, setProgressMessage] = useState("");


  const handlePredict = async () => {
    if (!ticker || !model) return;
    setLoading(true);
    setProgressMessage("🔄 Đang cập nhật dữ liệu...");
    setResult(null);

    try {
      // Gợi ý các bước người dùng dễ hiểu
      setProgressMessage("🧠 Đang huấn luyện mô hình...");
      const prediction = await predictStock(ticker, model);

      setProgressMessage("📈 Đang thực hiện dự đoán...");
      setTimeout(() => {
        setResult(prediction);
        setProgressMessage("");
        setLoading(false);
      }, 500); // delay nhỏ để UX mượt mà hơn
    } catch (error) {
      console.error("Lỗi dự đoán:", error);
      setProgressMessage("❌ Có lỗi xảy ra. Vui lòng thử lại.");
      setLoading(false);
    }
  };


  return (
    <div className={styles.container}>
      <h2>Dự đoán xu hướng cổ phiếu</h2>

      <div className={styles.formGroup}>
        <select
          className={styles.select}
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        >
          <option value="">Chọn mã cổ phiếu</option>
          {tickerOptions.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <select
          className={styles.select}
          value={model}
          onChange={(e) => setModel(e.target.value)}
        >
          {modelOptions.map((m) => (
            <option key={m} value={m}>
              {m === "random_forest" ? "Random Forest"
                : m === "xgboost" ? "XGBoost"
                : m === "lightgbm" ? "LightGBM"
                : m}
            </option>
          ))}
        </select>
        
        <button
          className={styles.button}
          onClick={handlePredict}
          disabled={!ticker || !model || loading}
        >
          {loading ? "Đang dự đoán..." : "Dự đoán"}
        </button>
      </div>

      {progressMessage && (
                        <div className={styles.progressMessage}>
                          {progressMessage}
                        </div>
                      )}
      {result && <PredictionResult result={result} />}
    </div>
  );
};

export default PredictionPage;






