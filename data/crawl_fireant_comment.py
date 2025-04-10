from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

# Đường dẫn tới ChromeDriver 
chrome_driver_path = "C:\\Program Files (x86)\\Web Drivers\\chrome\\chromedriver.exe"

# Khởi tạo trình duyệt Chrome
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Chạy ẩn nếu không muốn mở cửa sổ trình duyệt
options.add_argument("--disable-gpu")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Truy cập FireAnt
url = "https://fireant.vn/cong-dong/moi-nhat"
driver.get(url)

# Đợi pop-up xuất hiện và đóng nó
try:
    wait = WebDriverWait(driver, 1)
    close_popup_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Để sau')]"))
    )
    close_popup_button.click()
    print("✅ Đã đóng pop-up.")
except Exception as e:
    print("⚠ Không tìm thấy pop-up hoặc đã tự động đóng.")

# Mở file để lưu bình luận
comment_set = set()
num_scrolls = 30

# Biến đếm lỗi
error_count = 0
stale_error_count = 0

with open("comments.txt", "w", encoding="utf-8") as f:
    for scroll in range(num_scrolls):
        time.sleep(0.1)

        # Lấy danh sách bình luận hiện tại
        comment_elements = driver.find_elements(By.CSS_SELECTOR, "div.overflow-x-hidden.leading-7")
        time_elements = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.items-center.line-clamp-1 time")

        # Bỏ bình luận đầu tiên trong lần đầu tiên (thường là thông báo livestream)
        if scroll == 0 and comment_elements:
            comment_elements.pop(0)
            time_elements.pop(0)

        for i in range(min(len(comment_elements), len(time_elements))):
            try:
                # Click "Thêm" nếu có
                more_btns = comment_elements[i].find_elements(By.CSS_SELECTOR, "a.font-semibold.cursor-pointer")
                if more_btns:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_btns[0])
                    time.sleep(0.1)
                    driver.execute_script("arguments[0].click();", more_btns[0])
                    time.sleep(0.1)

                    # 🔄 Sau khi click, DOM thay đổi => phải lấy lại phần tử comment
                    comment_elements_updated = driver.find_elements(By.CSS_SELECTOR, "div.overflow-x-hidden.leading-7")
                    time_elements_updated = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.items-center.line-clamp-1 time")

                    if i >= len(comment_elements_updated) or i >= len(time_elements_updated):
                        continue

                    comment_text = comment_elements_updated[i].text.strip()
                    comment_time = time_elements_updated[i].get_attribute("title")
                else:
                    # Không có nút "Thêm"
                    comment_text = comment_elements[i].text.strip()
                    comment_time = time_elements[i].get_attribute("title")

                if comment_text and (comment_text, comment_time) not in comment_set:
                    comment_set.add((comment_text, comment_time))
                    f.write(f"[{comment_time}] {comment_text}\n\n")

            except Exception as e:
                error_count += 1
                if "stale element reference" in str(e).lower():
                    stale_error_count += 1
                print(f"⚠ Lỗi khi lấy bình luận {i}: {e}")

        # Cuộn xuống một đoạn nhỏ
        driver.execute_script("window.scrollBy(0, window.innerHeight);")

# In thống kê sau khi kết thúc
print(f"\n✅ Đã ghi {len(comment_set)} bình luận vào file comments.txt")
print(f"⚠ Tổng số lỗi: {error_count}")
print(f"⚠ Trong đó lỗi stale element: {stale_error_count}")

# Đóng trình duyệt
driver.quit()





