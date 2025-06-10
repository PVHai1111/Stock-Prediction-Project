// frontend/src/services/api.js

import axios from 'axios';

// Tạo instance axios với base URL mặc định
const API = axios.create({
  baseURL: "http://localhost:8000/api",
});

// ✅ Lấy danh sách tin tức theo mã cổ phiếu hoặc ngành, có hỗ trợ phân trang
export const fetchNews = async (
  ticker = "",
  page = 1,
  limit = 10,
  startDate = "",
  endDate = "",
  keyword = "",
  sentiment = "",
  sector = "" // Thêm trường sector
) => {
  try {
    const res = await API.get("/news", {
      params: {
        ticker,
        sector,
        page,
        limit,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        keyword: keyword || undefined,
        sentiment: sentiment || undefined,
      },
    });

    const results = Array.isArray(res?.data?.results) ? res.data.results : [];
    const total = typeof res?.data?.total === "number" ? res.data.total : 0;

    return { results, total };
  } catch (error) {
    console.error("❌ Lỗi khi gọi API /news:", error);
    return { results: [], total: 0 };
  }
};

// ✅ Lấy dữ liệu giá cổ phiếu
export const fetchPrice = async (ticker) => {
  const res = await API.get("/price", {
    params: { ticker },
  });
  return res.data;
};

// ✅ Dùng cho biểu đồ lịch sử giá
export const getPriceHistory = async (ticker, startDate = "", endDate = "") => {
  const res = await API.get("/price", {
    params: {
      ticker,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    },
  });
  return res.data;
};

// ✅ Gợi ý danh sách mã cổ phiếu để autocomplete
export const fetchTickers = async () => {
  const res = await API.get("/tickers");
  return res.data;
};

// ✅ Gọi API dự đoán tăng/giảm từ mô hình ML
export const predictStock = async (ticker, model = "random_forest") => {
  const res = await API.get("/predict", {
    params: { ticker, model },
  });
  return res.data;
};

// 🔄 Gọi API crawl và lưu dữ liệu giá
export const updatePrice = async (ticker) => {
  const res = await API.get("/price/update", {
    params: { ticker }
  });
  return res.data;
};

// ✅ Xuất CSV lịch sử giá cổ phiếu
export const exportPriceCSV = async (ticker, startDate, endDate) => {
  const params = new URLSearchParams({ ticker });
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);

  const response = await fetch(`/api/price/export?${params.toString()}`);
  if (!response.ok) throw new Error("Export CSV failed");

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${ticker}_price_history.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};











