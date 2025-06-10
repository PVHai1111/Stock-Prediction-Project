// src/pages/NewsPage/index.jsx
import React, { useEffect, useState } from "react";
import styles from "./NewsPage.module.css";
import StockInput from "../../components/ui/StockInput";
import { fetchNews } from "../../services/api";
import NewsCard from "../../components/ui/NewsCard";

const PAGE_SIZE = 10;

const NewsPage = () => {
  const [ticker, setTicker] = useState("");
  const [sector, setSector] = useState("");
  const [sectorList, setSectorList] = useState([]);

  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [keyword, setKeyword] = useState("");

  // Load danh sách ngành
  useEffect(() => {
    fetch("/sectors.json")
      .then((res) => res.json())
      .then((data) => setSectorList(data))
      .catch((err) => console.error("Lỗi tải danh sách ngành:", err));
  }, []);

  const loadArticles = async (
    tickerVal = "",
    pageVal = 1,
    sDate = "",
    eDate = "",
    kw = "",
    sectorVal = ""
  ) => {
    setLoading(true);
    try {
      const response = await fetchNews(
        tickerVal,
        pageVal,
        PAGE_SIZE,
        sDate,
        eDate,
        kw,
        "",          // ✅ fix: truyền đúng vị trí sentiment
        sectorVal    // ✅ fix: truyền đúng vị trí sector
      );

      const results = Array.isArray(response?.results) ? response.results : [];
      const total = typeof response?.total === "number" ? response.total : 0;

      setArticles(results);
      setTotal(total);
    } catch (err) {
      console.error("Lỗi tải tin tức:", err);
      setArticles([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadArticles(ticker, page, startDate, endDate, keyword, sector);
  }, [ticker, page, keyword, startDate, endDate, sector]);

  const handleSearch = () => {
    if (ticker.trim() === "" && keyword.trim() === "" && sector.trim() === "") {
      alert("Vui lòng nhập mã cổ phiếu, từ khóa hoặc chọn ngành.");
      return;
    }
    setPage(1);
    loadArticles(ticker, 1, startDate, endDate, keyword, sector);
  };

  const handleNextPage = () => {
    const next = page + 1;
    if ((next - 1) * PAGE_SIZE >= total) return;
    setPage(next);
  };

  const handlePrevPage = () => {
    const prev = page > 1 ? page - 1 : 1;
    setPage(prev);
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Tin tức theo mã cổ phiếu</h2>

      <StockInput
        value={ticker}
        onChange={setTicker}
        placeholder="Nhập mã như FPT..."
      />

      <input
        type="text"
        className={styles.keywordInput}
        placeholder="Từ khóa tiêu đề hoặc nội dung..."
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />

      <div className={styles.sectorFilterRow}>
        <label htmlFor="sector">Ngành:</label>
        <input
          list="sector-options"
          id="sector"
          className={styles.sectorSelect}
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          placeholder="Chọn ngành như ngành ngân hàng..."
        />
        <datalist id="sector-options">
          {sectorList.map((s, idx) => (
            <option key={idx} value={s} />
          ))}
        </datalist>
      </div>

      <div className={styles.dateFilterRow}>
        <label htmlFor="start">Từ ngày:</label>
        <input
          id="start"
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <label htmlFor="end">Đến ngày:</label>
        <input
          id="end"
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        <button className={styles.searchButton} onClick={handleSearch}>
          Tìm kiếm
        </button>
      </div>

      {loading ? (
        <p>Đang tải dữ liệu...</p>
      ) : articles.length === 0 ? (
        <p>Không có bài viết nào được tìm thấy.</p>
      ) : (
        <>
          <div className={styles.newsList}>
            {articles.map((article, index) => (
              <NewsCard key={index} article={article} />
            ))}
          </div>
          <div className={styles.pagination}>
            <button onClick={handlePrevPage} disabled={page === 1}>
              ← Trang trước
            </button>
            <span className={styles.pageNumber}>
              Trang {page} / {Math.ceil(total / PAGE_SIZE)}
            </span>
            <button
              onClick={handleNextPage}
              disabled={page * PAGE_SIZE >= total}
            >
              Trang sau →
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default NewsPage;












