import requests
from bs4 import BeautifulSoup
import json

url = "https://topi.vn/danh-sach-ma-chung-khoan-theo-nganh-tai-viet-nam.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table")
company_ticker_list = []
tickers_set = set()

for table in tables:
    rows = table.find_all("tr")[1:]  # Bỏ dòng tiêu đề
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            company = cols[0].get_text(strip=True)
            ticker = cols[1].get_text(strip=True)
            company_ticker_list.append({"company": company, "ticker": ticker})
            tickers_set.add(ticker)

# Ghi file JSON thông tin tên công ty và mã cổ phiếu
with open("company_ticker_list.json", "w", encoding="utf-8") as f:
    json.dump(company_ticker_list, f, ensure_ascii=False, indent=2)

# Ghi file TXT chứa các mã cổ phiếu dạng chuỗi
with open("tickers_string.txt", "w", encoding="utf-8") as f:
    f.write(", ".join([f'"{ticker}"' for ticker in sorted(tickers_set)]))

print("✅ Đã lưu danh sách mã cổ phiếu.")
