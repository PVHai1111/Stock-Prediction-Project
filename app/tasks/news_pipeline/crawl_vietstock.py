# app/tasks/news_pipeline/crawl_vietstock.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from app.db import SessionLocal
from app.models.news import News

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://vietstock.vn",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

def get_latest_links(limit: int = 3) -> set:
    db = SessionLocal()
    results = db.query(News).filter(News.source == "vietstock").order_by(News.published_time.desc()).limit(limit).all()
    db.close()
    return set(news.link.strip() for news in results if news.link)

def run(max_pages=3) -> list[dict]:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://vietstock.vn/chung-khoan.htm"
    driver.get(url)
    time.sleep(2)

    latest_links = get_latest_links()
    print(f"📌 Số bài gần nhất từ Vietstock đã lưu để kiểm tra trùng: {len(latest_links)}")

    articles = []
    seen_links = set()
    page = 1
    stop_crawling = False

    while page <= max_pages and not stop_crawling:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("div", class_="single_post_text")

        for item in items:
            try:
                title_tag = item.find("h4").find("a")
                title = title_tag.get_text(strip=True)
                link = "https://vietstock.vn" + title_tag["href"]
                if link in seen_links:
                    continue
                seen_links.add(link)

                if link in latest_links:
                    print(f"⛔ Gặp bài đã có trong DB: {link} → Dừng crawl.")
                    stop_crawling = True
                    break

                summary_tag = item.find("p", class_="post-p")
                summary = summary_tag.get_text(strip=True) if summary_tag else ""

                try:
                    res = requests.get(link, headers=HEADERS, timeout=10)
                    detail_soup = BeautifulSoup(res.content, "html.parser")

                    pub_raw = None
                    tag1 = detail_soup.find("p", class_="pPublishTimeSource right")
                    if tag1 and tag1.get_text(strip=True):
                        pub_raw = tag1.get_text(strip=True).lstrip("-").strip()
                    elif detail_soup.find("span", class_="date"):
                        pub_raw = detail_soup.find("span", class_="date").get_text(strip=True).strip()
                    elif detail_soup.find("span", class_="datenew"):
                        pub_raw = detail_soup.find("span", class_="datenew").get_text(strip=True).strip()
                    else:
                        print(f"⏭️ KHÔNG THẤY THẺ ngày đăng trong: {link}")
                        continue

                    try:
                        pub_dt = datetime.strptime(pub_raw, "%H:%M %d/%m/%Y")
                    except:
                        try:
                            pub_dt = datetime.strptime(pub_raw, "%d/%m/%Y %H:%M")
                        except:
                            try:
                                pub_dt = datetime.strptime(pub_raw, "%d-%m-%Y %H:%M:%S%z")
                                pub_dt = pub_dt.astimezone().replace(tzinfo=None)
                            except:
                                print(f"⏭️ Không parse được ngày: {pub_raw} ({link})")
                                continue

                    if pub_dt.year <= 2021:
                        print(f"🛑 Gặp bài từ {pub_dt.year} → Dừng crawl.")
                        stop_crawling = True
                        break

                    published_time = pub_dt.strftime("%Y-%m-%d %H:%M:%S")

                    content_block = detail_soup.find("div", {"data-role": "content"}) or \
                                    detail_soup.find("div", id="vst_detail")
                    paragraphs = content_block.find_all("p") if content_block else []
                    full_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

                    articles.append({
                        "title": title,
                        "link": link,
                        "published_time": published_time,
                        "summary": summary,
                        "price_change_info": "",
                        "category": "",
                        "sapo": "",
                        "content": full_text,
                        "source": "vietstock"
                    })

                    print(f"📝 [{len(articles)}] {title} - {published_time}")

                except Exception as e:
                    print(f"❌ Lỗi khi truy cập {link}: {e}")
                    continue

            except Exception as e:
                print(f"⚠️ Bỏ qua 1 bài: {e}")
                continue

        if not stop_crawling:
            try:
                next_btn = driver.find_element(By.XPATH, "//a[@title='Trang sau']")
                driver.execute_script("arguments[0].click();", next_btn)
                page += 1
                time.sleep(1.2)
            except:
                print("⛔ Không tìm thấy nút 'Trang sau' → dừng.")
                break

    driver.quit()
    print(f"\n✅ Đã thu thập {len(articles)} bài viết mới từ Vietstock.\n")
    return articles
