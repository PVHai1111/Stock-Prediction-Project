import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# === Đường dẫn dữ liệu và mô hình ===
data_path = "../data/merge_price_sentiment/FPT_final_training_data.csv"
model_path = "../app/ml_models/fpt_rf_model.joblib"

# === Đọc dữ liệu ===
df = pd.read_csv(data_path)

# === Tiền xử lý ===
df = df.dropna(subset=["Target_Label"])
df = df[df["Target_Label"] != 0].reset_index(drop=True)
print(f"✅ Tổng số mẫu còn lại sau lọc: {len(df)}")

# === Tạo đặc trưng và nhãn ===
features = ["positive", "neutral", "negative", "total_articles"]
X = df[features]
y = df["Target_Label"]

# === Chia tập huấn luyện và kiểm tra ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"📊 Số mẫu huấn luyện: {len(X_train)}")
print(f"📊 Số mẫu kiểm tra: {len(X_test)}")

# === Huấn luyện mô hình Random Forest ===
model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)

# === Dự đoán và đánh giá ===
y_pred = model.predict(X_test)
print("📋 Classification Report:")
print(classification_report(y_test, y_pred))

# === Lưu mô hình ===
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"✅ Mô hình đã được lưu tại: {model_path}")
