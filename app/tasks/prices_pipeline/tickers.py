# app/tasks/prices_pipeline/tickers.py
def load_tickers(path="data/tickers_string.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [t.strip().replace('"', '') for t in f.read().split(",") if t.strip()]
