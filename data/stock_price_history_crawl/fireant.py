# data/stock_price_history_crawl/fireant.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
import time
import os

# ===== Cấu hình =====
ticker = "MBB"
chrome_driver_path = "C:\\Program Files (x86)\\Web Drivers\\chrome\\chromedriver.exe"
max_date = datetime.strptime("2020-01-01", "%Y-%m-%d")

# ===== Khởi tạo trình duyệt =====
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
# options.add_argument("--headless")

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# ===== Truy cập trang mã cổ phiếu =====
url = f"https://fireant.vn/ma-chung-khoan/{ticker}"
driver.get(url)
time.sleep(2)

# ===== Đóng pop-up "Để sau" nếu có =====
try:
    wait = WebDriverWait(driver, 5)
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Để sau']")))
    close_button.click()
    print("✅ Đã đóng pop-up.")
    time.sleep(1)
except:
    print("⚠ Không có pop-up hoặc đã tự đóng.")

# ===== Nhấn vào tab “Dữ liệu” =====
try:
    data_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Dữ liệu']")))
    data_tab.click()
    print("✅ Đã chuyển sang tab Dữ liệu.")
    time.sleep(2)
except:
    print("❌ Không tìm thấy tab Dữ liệu.")
    driver.quit()
    exit()

# ===== Thu thập dữ liệu =====
data = []
seen_dates = set()

while True:
    new_dates_found = False
    rows = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.flex-1.w-full.py-2.border-b")

    for row in rows:
        try:
            items = row.find_elements(By.XPATH, "./div")
            if len(items) != 10:
                continue

            date_str = items[0].text.strip()
            if not date_str or date_str in seen_dates:
                continue

            parsed_date = datetime.strptime(date_str, "%d/%m/%Y")
            if parsed_date <= max_date:
                print(f"⛔ Đã gặp ngày giới hạn: {date_str}")
                new_dates_found = False
                break

            row_data = [item.text.strip() for item in items]
            data.append(row_data)
            seen_dates.add(date_str)
            new_dates_found = True
        except Exception:
            continue

    if not new_dates_found:
        print("✅ Không còn ngày mới → Dừng lại.")
        break

    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(0.05)

# ===== Lưu kết quả =====
df = pd.DataFrame(data, columns=[
    "Date", "Change", "Percent Change", "Open", "High", "Low",
    "Close", "Average", "Volume", "Value"
])

os.makedirs("stock_price_history_crawl", exist_ok=True)
filename = f"stock_price_history_crawl/{ticker}_historical_data.csv"
df.to_csv(filename, index=False)

print(f"✅ Đã lưu {len(df)} dòng dữ liệu vào: {filename}")
driver.quit()
print("✅ Trình duyệt đã đóng.")




