import requests
from bs4 import BeautifulSoup
import json

# Bản đồ ánh xạ từ tiêu đề h3 sang tên ngành cần lưu
sector_mapping = {
    "1. Nhóm cổ phiếu ngành ngân hàng": "ngành ngân hàng",
    "2. Nhóm cổ phiếu chứng khoán": "ngành chứng khoán",
    "3. Nhóm cổ phiếu ngành điện": "ngành điện",
    "4. Cổ phiếu ngành dầu khí": "ngành dầu khí",
    "5. Cổ phiếu ngành du lịch": "ngành du lịch",
    "6. Cổ phiếu ngành bán lẻ": "ngành bán lẻ",
    "7. Cổ phiếu đầu tư công": "đầu tư công",
    "8. Nhóm cổ phiếu ngành thép": "ngành thép",
    "9. Nhóm cổ phiếu ngành hàng không": "ngành hàng không",
    "10. Nhóm cổ phiếu ngành y tế": "ngành y tế",
    "11. Nhóm cổ phiếu ngành thuỷ hải sản": "ngành thuỷ hải sản",
    "12. Nhóm cổ phiếu ngành dệt may - may mặc": "ngành dệt may",
    "13. Ngành giao thông vận tải": "ngành giao thông vận tải",
    "14. Nhóm cổ phiếu ngành bảo hiểm": "ngành bảo hiểm",
    "15. Nhóm cổ phiếu ngành công nghệ": "ngành công nghệ",
    "16. Nhóm cổ phiếu ngành than - khoáng sản": "ngành than khoáng sản",
    "17. Nhóm cổ phiếu ngành xây dựng": "ngành xây dựng",
    "18. Nhóm cổ phiếu ngành thực phẩm": "ngành thực phẩm",
    "19. Nhóm cổ phiếu ngành bưu chính viễn thông": "ngành bưu chính viễn thông",
    "20. Nhóm cổ phiếu ngành truyền thông - giải trí": "ngành truyền thông",
    "21. Nhóm cổ phiếu ngành cao su": "ngành cao su"
}

url = "https://topi.vn/danh-sach-ma-chung-khoan-theo-nganh-tai-viet-nam.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

company_ticker_list = []
tickers_set = set()

# Lặp qua từng h3 (nhóm ngành)
for h3 in soup.find_all("h3"):
    h3_text = h3.get_text(strip=True)
    sector = sector_mapping.get(h3_text)

    if not sector:
        continue  # Bỏ qua các h3 không thuộc 21 nhóm ngành

    # Lặp qua các thẻ phía sau cho đến khi gặp <h3> khác (bắt đầu nhóm ngành mới)
    next_tag = h3.find_next_sibling()
    while next_tag and next_tag.name != "h3":
        if next_tag.name == "table":
            rows = next_tag.find_all("tr")[1:]  # Bỏ dòng tiêu đề
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    company = cols[0].get_text(strip=True)
                    ticker = cols[1].get_text(strip=True)
                    if company and ticker:
                        company_ticker_list.append({
                            "company": company,
                            "ticker": ticker,
                            "sector": sector
                        })
                        tickers_set.add(ticker)
        next_tag = next_tag.find_next_sibling()

# Ghi file JSON thông tin tên công ty, mã cổ phiếu và ngành
with open("company_ticker_list.json", "w", encoding="utf-8") as f:
    json.dump(company_ticker_list, f, ensure_ascii=False, indent=2)

# Ghi file TXT chứa các mã cổ phiếu dạng chuỗi
with open("tickers_string.txt", "w", encoding="utf-8") as f:
    f.write(", ".join([f'"{ticker}"' for ticker in sorted(tickers_set)]))

print(f"✅ Đã lưu {len(company_ticker_list)} công ty vào company_ticker_list.json.")
