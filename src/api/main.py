"""
FastAPI service for the Walmart M5 forecasting and pricing project.

This API exposes the reusable production modules created from the
finalized notebooks.

Endpoints:
- GET  /health
- POST /forecast
- POST /recommend-price

Important development limitation:
The current feature table contains daily-updated lag/rolling features.
Therefore this API currently serves predictions for rows that already
exist in the processed feature dataset. It is not yet a strict one-shot
future 28-day forecasting service.

A future production version should add recursive or horizon-safe feature
generation for dates beyond the historical feature table.
"""

from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.forecasting.predict import (
    create_prediction_output,
    load_model_artifacts,
    predict_demand,
)
from src.pricing.recommend_price import (
    create_pricing_base,
    estimate_item_elasticities,
    generate_recommendations,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

FEATURE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features_CA_1_200_items.csv"
)


# ============================================================
# APPLICATION STATE
# These objects are loaded once when the API starts.
# ============================================================

feature_df: pd.DataFrame | None = None
forecast_pipeline = None
model_metadata: dict | None = None
item_elasticity: pd.DataFrame | None = None


# ============================================================
# REQUEST / RESPONSE SCHEMAS
# ============================================================

class ForecastRequest(BaseModel):
    item_id: str = Field(
        ...,
        examples=["FOODS_1_001"],
    )
    store_id: str = Field(
        ...,
        examples=["CA_1"],
    )
    forecast_date: date = Field(
        ...,
        examples=["2016-05-23"],
    )


class ForecastResponse(BaseModel):
    date: str
    item_id: str
    store_id: str
    predicted_units: float
    current_price: float | None = None


class PricingRequest(BaseModel):
    item_id: str = Field(
        ...,
        examples=["FOODS_1_001"],
    )
    store_id: str = Field(
        ...,
        examples=["CA_1"],
    )
    forecast_date: date = Field(
        ...,
        examples=["2016-05-23"],
    )


class PricingResponse(BaseModel):
    date: str
    item_id: str
    store_id: str

    predicted_units: float

    current_price: float
    recommended_price: float
    recommended_change_pct: float

    expected_demand: float

    current_expected_revenue: float
    recommended_expected_revenue: float
    simulated_revenue_lift: float
    simulated_revenue_lift_pct: float | None

    elasticity: float
    elasticity_source: str
    elasticity_observations: int

    pricing_action: str
    recommendation_actionable: bool


# ============================================================
# STARTUP
# Load model, metadata, features, and elasticity assumptions once.
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global feature_df
    global forecast_pipeline
    global model_metadata
    global item_elasticity

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Feature file not found: {FEATURE_FILE}"
        )

    feature_df = pd.read_csv(
        FEATURE_FILE,
        parse_dates=["date"],
        low_memory=False,
    )

    forecast_pipeline, model_metadata = (
        load_model_artifacts(
            PROJECT_ROOT
        )
    )

    item_elasticity = (
        estimate_item_elasticities(
            feature_df
        )
    )

    print(
        "API startup complete."
    )

    print(
        "Feature rows:",
        f"{len(feature_df):,}",
    )

    print(
        "Elasticity rows:",
        f"{len(item_elasticity):,}",
    )

    print(
        "Forecast model:",
        model_metadata[
            "selected_model"
        ],
    )

    yield

    print(
        "API shutdown complete."
    )


app = FastAPI(
    title="Walmart Demand Forecasting & Dynamic Pricing API",
    description=(
        "Development API for demand forecasting and "
        "scenario-based dynamic pricing using the Walmart M5 project."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# HELPERS
# ============================================================

def get_feature_row(
    item_id: str,
    store_id: str,
    forecast_date: date,
) -> pd.DataFrame:
    """
    Find the exact model-ready feature row requested by the API user.
    """

    if feature_df is None:
        raise RuntimeError(
            "Feature data has not been loaded."
        )

    requested_date = pd.Timestamp(
        forecast_date
    )

    matching_rows = feature_df.loc[
        (feature_df["item_id"] == item_id)
        & (
            feature_df["store_id"]
            == store_id
        )
        & (
            feature_df["date"]
            == requested_date
        )
    ].copy()

    if matching_rows.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "No model-ready feature row found for "
                f"item_id={item_id}, "
                f"store_id={store_id}, "
                f"date={forecast_date}. "
                "The current API only supports dates already "
                "present in the processed feature dataset."
            ),
        )

    if len(matching_rows) > 1:
        raise HTTPException(
            status_code=500,
            detail=(
                "Multiple feature rows were found for the "
                "same date-item-store key."
            ),
        )

    return matching_rows


def forecast_one_row(
    row: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run the trained forecasting pipeline for one model-ready row.
    """

    if (
        forecast_pipeline is None
        or model_metadata is None
    ):
        raise RuntimeError(
            "Forecast model has not been loaded."
        )

    predictions = predict_demand(
        feature_df=row,
        forecast_pipeline=forecast_pipeline,
        metadata=model_metadata,
    )

    return create_prediction_output(
        feature_df=row,
        predictions=predictions,
    )


def safe_float(
    value,
) -> float | None:
    """
    Convert a value to a JSON-safe float.
    NaN becomes None.
    """

    if pd.isna(value):
        return None

    return float(value)


# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
def health():
    """
    Basic service health check.
    """

    ready = (
        feature_df is not None
        and forecast_pipeline is not None
        and model_metadata is not None
        and item_elasticity is not None
    )

    return {
        "status": (
            "healthy"
            if ready
            else "not_ready"
        ),
        "feature_rows": (
            len(feature_df)
            if feature_df is not None
            else 0
        ),
        "model": (
            model_metadata.get(
                "selected_model"
            )
            if model_metadata
            else None
        ),
    }


@app.post(
    "/forecast",
    response_model=ForecastResponse,
)
def forecast(
    request: ForecastRequest,
):
    """
    Predict demand for one existing model-ready date-item-store row.
    """

    row = get_feature_row(
        item_id=request.item_id,
        store_id=request.store_id,
        forecast_date=request.forecast_date,
    )

    prediction_output = (
        forecast_one_row(
            row
        )
    )

    result = prediction_output.iloc[0]

    return ForecastResponse(
        date=str(
            pd.Timestamp(
                result["date"]
            ).date()
        ),
        item_id=str(
            result["item_id"]
        ),
        store_id=str(
            result["store_id"]
        ),
        predicted_units=float(
            result["prediction"]
        ),
        current_price=safe_float(
            result.get(
                "sell_price"
            )
        ),
    )


@app.post(
    "/recommend-price",
    response_model=PricingResponse,
)
def recommend_price(
    request: PricingRequest,
):
    """
    Forecast demand and return one guarded scenario-based price recommendation.
    """

    if item_elasticity is None:
        raise RuntimeError(
            "Elasticity assumptions have not been loaded."
        )

    row = get_feature_row(
        item_id=request.item_id,
        store_id=request.store_id,
        forecast_date=request.forecast_date,
    )

    prediction_output = (
        forecast_one_row(
            row
        )
    )

    current_price = (
        prediction_output.iloc[0][
            "sell_price"
        ]
    )

    if (
        pd.isna(current_price)
        or current_price <= 0
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "A valid positive sell_price is required "
                "for pricing recommendations."
            ),
        )

    pricing_base = (
        create_pricing_base(
            predictions_df=prediction_output,
            item_elasticity=item_elasticity,
        )
    )

    pricing_results = (
        generate_recommendations(
            pricing_base
        )
    )

    result = pricing_results.iloc[0]

    lift_pct = (
        safe_float(
            result[
                "expected_revenue_lift_pct"
            ]
        )
    )

    return PricingResponse(
        date=str(
            pd.Timestamp(
                result["date"]
            ).date()
        ),
        item_id=str(
            result["item_id"]
        ),
        store_id=str(
            result["store_id"]
        ),

        predicted_units=float(
            result["prediction"]
        ),

        current_price=float(
            result["sell_price"]
        ),
        recommended_price=float(
            result["recommended_price"]
        ),
        recommended_change_pct=float(
            result["recommended_change_pct"]
        ),

        expected_demand=float(
            result["expected_demand"]
        ),

        current_expected_revenue=float(
            result[
                "current_expected_revenue"
            ]
        ),
        recommended_expected_revenue=float(
            result[
                "expected_revenue"
            ]
        ),
        simulated_revenue_lift=float(
            result[
                "expected_revenue_lift"
            ]
        ),
        simulated_revenue_lift_pct=lift_pct,

        elasticity=float(
            result["usable_elasticity"]
        ),
        elasticity_source=str(
            result["elasticity_source"]
        ),
        elasticity_observations=int(
            result[
                "elasticity_observations"
            ]
        ),

        pricing_action=str(
            result["pricing_action"]
        ),
        recommendation_actionable=bool(
            result[
                "recommendation_actionable"
            ]
        ),
    )


# ============================================================
# LOCAL DEVELOPMENT
# Allows:
# python -m src.api.main
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
