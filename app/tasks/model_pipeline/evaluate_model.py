# app/tasks/model_pipeline/evaluate_model.py
from app.tasks.model_pipeline.models import random_forest, xgboost, lightgbm
import pandas as pd
from app.tasks.model_pipeline.feature_config import FEATURE_COLUMNS

def evaluate_all_models(df: pd.DataFrame):
    X = df[FEATURE_COLUMNS]
    y = df["label"]

    for name, module in {
        "rf": random_forest,
        "xgb": xgboost,
        "lgbm": lightgbm
    }.items():
        print(f"📊 Evaluating {name.upper()}")
        model = module.train_and_evaluate(X, y)
