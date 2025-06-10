# app/tasks/model_pipeline/train_model.py

from app.tasks.model_pipeline.models import random_forest, xgboost, lightgbm
from app.tasks.model_pipeline.feature_config import FEATURE_COLUMNS


def train_model_for_ticker(ticker: str, df):
    X = df[FEATURE_COLUMNS].copy()
    y = df["label"]

    for model_name, model_module in {
        "rf": random_forest,
        "xgb": xgboost,
        "lgbm": lightgbm,
    }.items():
        print(f"=== Training {model_name.upper()} ===")
        model = model_module.train_and_evaluate(X, y)
        model_module.save_model(model, FEATURE_COLUMNS, ticker)









