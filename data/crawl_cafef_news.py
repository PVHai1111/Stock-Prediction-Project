from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import os
import json
import requests
from datetime import datetime

# ==== Cấu hình Chrome Driver ====
chrome_driver_path = "C:\\Program Files (x86)\\Web Drivers\\chrome\\chromedriver.exe"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# ==== Truy cập trang CafeF ====
url = "https://cafef.vn/thi-truong-chung-khoan.chn"
driver.get(url)
time.sleep(2)

# ==== Tạo thư mục lưu dữ liệu ====
today = datetime.today().strftime('%Y-%m-%d')
save_dir = f"cafef_articles/{today}"
os.makedirs(save_dir, exist_ok=True)

# ==== Bước 1: Crawl danh sách bài viết ====
combined_articles = []
seen_links = set()
max_clicks = 1800
clicked = 0

while clicked < max_clicks:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.find_all("div", class_="tlitem box-category-item")

    new_found = 0

    for item in items:
        try:
            title_tag = item.find("h3").find("a")
            title = title_tag.text.strip()
            link = "https://cafef.vn" + title_tag['href']

            if link in seen_links:
                continue

            seen_links.add(link)

            time_tag = item.find("span", class_="time time-ago")
            timestamp = time_tag['title'] if time_tag else "Unknown"
            summary_tag = item.find("p", class_="sapo box-category-sapo")
            summary = summary_tag.text.strip() if summary_tag else ""

            combined_articles.append({
                "title": title,
                "link": link,
                "published_time": timestamp,
                "summary": summary
            })

            # 🔥 Xóa thẻ bài viết khỏi DOM bằng JavaScript
            item_id = item.get("id")
            if item_id:
                driver.execute_script(f"""
                    var el = document.getElementById("{item_id}");
                    if (el) el.remove();
                """)
            else:
                # Nếu không có ID, xoá trực tiếp theo element
                driver.execute_script("""
                    arguments[0].remove();
                """, driver.find_element(By.XPATH, f"//a[@href='{title_tag['href']}']/ancestor::div[contains(@class, 'tlitem')]"))
                
        except Exception as e:
            print("⚠️ Bỏ qua một bài do lỗi:", e)


    try:
        btn = driver.find_element(By.CLASS_NAME, "btn-viewmore")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.001)
        clicked += 1
    except:
        print("⛔ Không thể click 'Xem thêm'. Dừng lại.")
        break

driver.quit()

# ==== Bước 2: Crawl nội dung chi tiết ====
for i, article in enumerate(combined_articles):
    link = article["link"]
    try:
        res = requests.get(link, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        pub_time = soup.select_one("p.dateandcat span.pdate").get_text(strip=True)
        category = soup.select_one("p.dateandcat a.category-page__name").get_text(strip=True)
        sapo = soup.find("h2", class_="sapo")
        sapo_text = sapo.get_text(strip=True) if sapo else ""

        content_block = soup.find("div", {"data-role": "content"})
        paragraphs = content_block.find_all("p") if content_block else []
        full_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        article.update({
            "published_time": pub_time,
            "category": category,
            "sapo": sapo_text,
            "content": full_text
        })

        print(f"📝 [{i+1}/{len(combined_articles)}] {article['title']}")
        time.sleep(0.001)

    except Exception as e:
        print(f"❌ Lỗi bài {link}: {e}")

# ==== Lưu tất cả vào 1 file duy nhất ====
combined_path = os.path.join(save_dir, "articles_combined_temp.json")
with open(combined_path, "w", encoding="utf-8") as f:
    json.dump(combined_articles, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã lưu {len(combined_articles)} bài viết đầy đủ vào {combined_path}")




