"""
Reusable demand forecasting for the Walmart M5 project.

This module loads the trained forecasting pipeline created in Notebook 04
and applies it to model-ready feature rows.

Important:
- This file performs model inference only.
- It expects the same feature columns used during training.
- Historical lag/rolling features must already be created safely.
- Predictions are clipped at zero because unit demand cannot be negative.
- This is currently a daily-updated inference workflow, not yet a strict
  recursive multi-step 28-day production forecast.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


DEFAULT_MODEL_FILENAME = "demand_forecast_model.joblib"
DEFAULT_METADATA_FILENAME = "demand_forecast_model_metadata.json"


def load_model_artifacts(
    project_root: Path,
):
    """
    Load the trained forecasting pipeline and its metadata.

    Returns
    -------
    tuple
        (forecast_pipeline, metadata)
    """

    project_root = Path(project_root)

    model_dir = (
        project_root
        / "models"
    )

    model_file = (
        model_dir
        / DEFAULT_MODEL_FILENAME
    )

    metadata_file = (
        model_dir
        / DEFAULT_METADATA_FILENAME
    )

    if not model_file.exists():
        raise FileNotFoundError(
            f"Forecast model not found: {model_file}"
        )

    if not metadata_file.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {metadata_file}"
        )

    forecast_pipeline = joblib.load(
        model_file
    )

    with open(
        metadata_file,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    return forecast_pipeline, metadata


def validate_metadata(
    metadata: dict,
) -> None:
    """
    Confirm the saved model metadata contains the fields
    needed for safe inference.
    """

    required_keys = [
        "selected_model",
        "target",
        "feature_columns",
        "categorical_features",
        "numeric_features",
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in metadata
    ]

    if missing_keys:
        raise ValueError(
            "Model metadata is missing required keys: "
            f"{missing_keys}"
        )


def validate_prediction_input(
    feature_df: pd.DataFrame,
    metadata: dict,
) -> None:
    """
    Validate that the incoming DataFrame contains every
    feature expected by the trained model.
    """

    validate_metadata(
        metadata
    )

    required_features = (
        metadata["feature_columns"]
    )

    missing_features = [
        column
        for column in required_features
        if column not in feature_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Prediction data is missing trained features: "
            f"{missing_features}"
        )

    if feature_df.empty:
        raise ValueError(
            "Prediction data is empty."
        )


def prepare_prediction_features(
    feature_df: pd.DataFrame,
    metadata: dict,
) -> pd.DataFrame:
    """
    Select the exact training features and reproduce the
    categorical preprocessing used in Notebook 04.

    The saved sklearn Pipeline performs encoding internally,
    but categorical missing values were converted to the
    string '__MISSING__' before model fitting. We reproduce
    that same step here.
    """

    validate_prediction_input(
        feature_df=feature_df,
        metadata=metadata,
    )

    feature_columns = (
        metadata["feature_columns"]
    )

    categorical_features = (
        metadata["categorical_features"]
    )

    X = feature_df[
        feature_columns
    ].copy()

    existing_categorical = [
        column
        for column in categorical_features
        if column in X.columns
    ]

    if existing_categorical:
        X[
            existing_categorical
        ] = (
            X[
                existing_categorical
            ]
            .fillna("__MISSING__")
            .astype(str)
        )

    return X


def predict_demand(
    feature_df: pd.DataFrame,
    forecast_pipeline,
    metadata: dict,
) -> np.ndarray:
    """
    Predict non-negative unit demand for model-ready rows.
    """

    X = prepare_prediction_features(
        feature_df=feature_df,
        metadata=metadata,
    )

    predictions = forecast_pipeline.predict(
        X
    )

    predictions = np.clip(
        np.asarray(predictions, dtype=float),
        0,
        None,
    )

    if len(predictions) != len(feature_df):
        raise ValueError(
            "Prediction count does not match input row count."
        )

    if not np.isfinite(
        predictions
    ).all():
        raise ValueError(
            "Non-finite demand predictions were produced."
        )

    return predictions


def create_prediction_output(
    feature_df: pd.DataFrame,
    predictions: np.ndarray,
) -> pd.DataFrame:
    """
    Build a clean prediction table for downstream pricing,
    APIs, dashboards, or batch outputs.
    """

    identifier_candidates = [
        "date",
        "item_id",
        "store_id",
        "state_id",
        "dept_id",
        "cat_id",
        "units_sold",
        "sell_price",
    ]

    identifier_columns = [
        column
        for column in identifier_candidates
        if column in feature_df.columns
    ]

    output = feature_df[
        identifier_columns
    ].copy()

    output["prediction"] = (
        predictions
    )

    return output


def predict_dataframe(
    feature_df: pd.DataFrame,
    project_root: Path,
) -> pd.DataFrame:
    """
    High-level forecasting function.

    Load model artifacts, validate the input, predict demand,
    and return a clean prediction DataFrame.
    """

    forecast_pipeline, metadata = (
        load_model_artifacts(
            project_root
        )
    )

    predictions = predict_demand(
        feature_df=feature_df,
        forecast_pipeline=forecast_pipeline,
        metadata=metadata,
    )

    prediction_output = (
        create_prediction_output(
            feature_df=feature_df,
            predictions=predictions,
        )
    )

    return prediction_output


def predict_from_csv(
    feature_file: Path,
    project_root: Path,
) -> pd.DataFrame:
    """
    Load a processed feature CSV and generate predictions.
    """

    feature_file = Path(
        feature_file
    )

    if not feature_file.exists():
        raise FileNotFoundError(
            f"Feature file not found: {feature_file}"
        )

    feature_df = pd.read_csv(
    feature_file,
    parse_dates=["date"],
    low_memory=False,
    )

    return predict_dataframe(
        feature_df=feature_df,
        project_root=project_root,
    )


def save_predictions(
    predictions_df: pd.DataFrame,
    project_root: Path,
    filename: str = "latest_predictions.csv",
) -> Path:
    """
    Save forecast output for downstream pricing and application use.
    """

    project_root = Path(
        project_root
    )

    output_dir = (
        project_root
        / "outputs"
        / "forecasting"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / filename
    )

    predictions_df.to_csv(
        output_file,
        index=False,
    )

    return output_file


def run_forecast(
    project_root: Path,
    feature_file: Path,
    save_output: bool = True,
    output_filename: str = "latest_predictions.csv",
) -> pd.DataFrame:
    """
    Convenience function for batch inference.

    feature CSV -> trained model -> demand predictions -> optional CSV
    """

    project_root = Path(
        project_root
    )

    predictions_df = predict_from_csv(
        feature_file=feature_file,
        project_root=project_root,
    )

    if save_output:
        output_file = save_predictions(
            predictions_df=predictions_df,
            project_root=project_root,
            filename=output_filename,
        )

        print(
            "Saved:",
            output_file,
        )

    print(
        "Prediction rows:",
        f"{len(predictions_df):,}",
    )

    print(
        "Predicted demand range:",
        f"{predictions_df['prediction'].min():.3f}",
        "to",
        f"{predictions_df['prediction'].max():.3f}",
    )

    print(
        "PASS: demand forecasting complete"
    )

    return predictions_df


if __name__ == "__main__":

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

    run_forecast(
        project_root=PROJECT_ROOT,
        feature_file=FEATURE_FILE,
        save_output=True,
    )