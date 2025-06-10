# app/tasks/prices_pipeline/crawl_prices.py
import time
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_prices_for_ticker(ticker: str, max_date: date) -> list[list[str]]:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")

    service = Service()  # ChromeDriver phải nằm trong PATH
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = f"https://fireant.vn/ma-chung-khoan/{ticker}"
        driver.get(url)
        time.sleep(0.1)

        # Đóng popup
        try:
            WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Để sau']"))
            ).click()
            time.sleep(0.1)
        except:
            pass

        # Mở tab "Dữ liệu"
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Dữ liệu']"))
            ).click()
            time.sleep(0.1)
        except:
            print("❌ Không tìm thấy tab Dữ liệu.")
            return []

        data = []
        seen_dates = set()

        while True:
            rows = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.flex-1.w-full.py-2.border-b")
            new_found = False

            for row in rows:
                items = row.find_elements(By.XPATH, "./div")
                if len(items) != 10:
                    continue

                date_str = items[0].text.strip()
                if not date_str or date_str in seen_dates:
                    continue

                try:
                    parsed_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                except:
                    continue

                if parsed_date <= max_date:
                    print(f"⛔ Đã gặp ngày đã có trong DB: {date_str}")
                    return data

                row_data = [item.text.strip() for item in items]
                data.append(row_data)
                seen_dates.add(date_str)
                new_found = True

            if not new_found:
                print("✅ Không còn ngày mới → Dừng lại.")
                break

            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.05)

        return data
    finally:
        driver.quit()


