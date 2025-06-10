// src/routes/AppRoutes.jsx

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Import các trang
import NewsPage from "../pages/NewsPage";
import PriceHistoryPage from "../pages/PriceHistoryPage";
import PredictionPage from "../pages/PredictionPage";

const AppRoutes = () => {
  return (
    <Routes>
      {/* Chuyển hướng root về /news */}
      <Route path="/" element={<Navigate to="/news" replace />} />
      <Route path="/news" element={<NewsPage />} />
      <Route path="/price" element={<PriceHistoryPage />} />
      <Route path="/predict" element={<PredictionPage />} />
      {/* Route mặc định nếu không khớp */}
      <Route path="*" element={<h2>404 - Trang không tồn tại</h2>} />
    </Routes>
  );
};

export default AppRoutes;
