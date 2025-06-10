# app/tasks/news_pipeline/crawl_cafef.py

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import requests
import time
from app.db import SessionLocal
from app.models.news import News

def get_latest_links(limit: int = 3) -> set:
    """Lấy danh sách các link gần nhất đã lưu trong DB để kiểm tra trùng."""
    db = SessionLocal()
    results = db.query(News).order_by(News.published_time.desc()).limit(limit).all()
    db.close()
    return set(news.link.strip() for news in results if news.link)

def run(max_clicks=1700) -> list[dict]:
    # ==== Cấu hình Chrome ====
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")
    service = Service()  # ChromeDriver cần nằm trong PATH
    driver = webdriver.Chrome(service=service, options=options)

    # ==== Truy cập trang CafeF ====
    url = "https://cafef.vn/thi-truong-chung-khoan.chn"
    driver.get(url)
    time.sleep(2)

    latest_links = get_latest_links()
    print(f"📌 Số bài mới nhất trong DB được kiểm tra: {len(latest_links)}")

    articles = []
    seen_links = set()
    clicked = 0
    stop_crawling = False

    while clicked < max_clicks and not stop_crawling:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.tlitem.box-category-item")

        for item in items:
            try:
                title_tag = item.find("h3").find("a")
                title = title_tag.text.strip()
                link = "https://cafef.vn" + title_tag['href']
                if link in seen_links:
                    continue
                seen_links.add(link)

                if link in latest_links:
                    print(f"⛔ Gặp bài đã có trong DB: {link} → Dừng crawl.")
                    stop_crawling = True
                    break

                time_tag = item.find("span", class_="time time-ago hidden") or item.find("span", class_="time time-ago")
                timestamp = time_tag['title'] if time_tag else "Unknown"

                summary_tag = item.find("p", class_="sapo box-category-sapo")
                summary = summary_tag.text.strip() if summary_tag else ""

                price_tag = item.find("p", class_="top5_news_mack magiaodich")
                price_change_info = price_tag.get_text(strip=True) if price_tag else ""

                # === Truy cập chi tiết bài viết ===
                try:
                    res = requests.get(link, timeout=10)
                    soup_detail = BeautifulSoup(res.content, "html.parser")

                    pub_time = soup_detail.select_one("p.dateandcat span.pdate")
                    category = soup_detail.select_one("p.dateandcat a.category-page__name")
                    sapo = soup_detail.find("h2", class_="sapo")
                    content_div = soup_detail.find("div", {"data-role": "content"})

                    content = "\n".join([
                        p.get_text(strip=True) for p in content_div.find_all("p")
                        if p.get_text(strip=True)
                    ]) if content_div else ""

                    articles.append({
                        "title": title,
                        "link": link,
                        "published_time": pub_time.get_text(strip=True) if pub_time else timestamp,
                        "summary": summary,
                        "price_change_info": price_change_info,
                        "category": category.get_text(strip=True) if category else "",
                        "sapo": sapo.get_text(strip=True) if sapo else "",
                        "content": content,
                        "source": "cafef"
                    })

                    print(f"📝 [{len(articles)}] {title}")

                except Exception as e:
                    print(f"❌ Lỗi khi tải chi tiết bài {link}: {e}")
                    continue

                # Gỡ bài khỏi DOM để giảm lag
                item_id = item.get("id")
                try:
                    if item_id:
                        driver.execute_script(f"""
                            var el = document.getElementById("{item_id}");
                            if (el) el.remove();
                        """)
                    else:
                        driver.execute_script("""
                            arguments[0].remove();
                        """, driver.find_element(By.XPATH, f"//a[@href='{title_tag['href']}']/ancestor::div[contains(@class, 'tlitem')]"))
                except:
                    pass

            except Exception as e:
                print("⚠️ Bỏ qua bài do lỗi:", e)

        if not stop_crawling:
            try:
                btn = driver.find_element(By.CLASS_NAME, "btn-viewmore")
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.4)
                clicked += 1
            except:
                print("⛔ Không thể click 'Xem thêm'. Dừng lại.")
                break

    driver.quit()
    print(f"\n✅ Đã thu thập {len(articles)} bài viết mới từ CafeF.\n")
    return articles

