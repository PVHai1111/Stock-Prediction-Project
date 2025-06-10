# code/count_tickers.py

def count_tickers(file_path="data/tickers_string.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        tickers = [t.strip().replace('"', '') for t in f.read().split(",") if t.strip()]
    print(f"Số lượng mã cổ phiếu trong {file_path}: {len(tickers)}")

if __name__ == "__main__":
    count_tickers()
