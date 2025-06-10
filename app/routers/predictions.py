# app/routers/predictions.py

from fastapi import APIRouter, HTTPException, Query
from app.tasks.model_pipeline.run_prediction_pipeline import run_prediction_pipeline

router = APIRouter(prefix="/api")

@router.get("/predict")
def predict_by_ticker(
    ticker: str = Query(..., min_length=1),
    model: str = Query("random_forest", pattern="^(random_forest|xgboost|lightgbm)$")
):
    try:
        result = run_prediction_pipeline(ticker.upper(), model)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "ticker": result.get("ticker"),
        "model": result.get("model"),
        "prediction": result.get("prediction", "Không xác định"),
        "confidence": result.get("confidence", None),
        "input_features": result.get("features", {}),
        "feature_importance": result.get("feature_importance", {}),
        "latest_close": result.get("latest_close", None),
        "date": str(result.get("date", "")),
        "latest_articles": result.get("latest_articles", []),
    }





