"""
Reusable dynamic-pricing logic for the Walmart M5 project.

This module moves the finalized pricing logic from Notebook 06 into
production-style Python functions.

Important:
- The demand forecast provides the baseline demand estimate.
- Price response is handled separately through an observational/fallback
  elasticity assumption.
- Revenue lift is simulated, not a causal business result.
- Candidate prices are constrained to +/-10% around the current price.
- If several prices produce effectively equal expected revenue, the
  current/closest price is preferred to avoid unnecessary price changes.
"""

from pathlib import Path

import numpy as np
import pandas as pd


PRICE_CHANGE_OPTIONS = np.array([
    -0.10,
    -0.075,
    -0.05,
    -0.025,
    0.00,
    0.025,
    0.05,
    0.075,
    0.10,
])

PRICE_FLOOR = 0.01

MIN_ELASTICITY_OBSERVATIONS = 3
FALLBACK_ELASTICITY = -1.0

REVENUE_TOLERANCE_PCT = 0.001
MIN_REVENUE_LIFT_PCT = 0.01


def validate_pricing_history(
    feature_df: pd.DataFrame,
) -> None:
    """
    Validate the historical feature data needed to estimate elasticity.
    """

    required_columns = [
        "date",
        "item_id",
        "store_id",
        "units_sold",
        "sell_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in feature_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Pricing history is missing required columns: "
            f"{missing_columns}"
        )

    if feature_df.empty:
        raise ValueError(
            "Pricing history is empty."
        )


def build_weekly_price_history(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate daily product-store observations into weekly price/demand
    observations used for the development elasticity estimate.
    """

    validate_pricing_history(
        feature_df
    )

    pricing_history = feature_df[
        [
            "date",
            "item_id",
            "store_id",
            "units_sold",
            "sell_price",
        ]
    ].copy()

    pricing_history["date"] = pd.to_datetime(
        pricing_history["date"]
    )

    pricing_history = pricing_history.loc[
        pricing_history["sell_price"].notna()
        & (pricing_history["sell_price"] > 0)
    ].copy()

    pricing_history["week_start"] = (
        pricing_history["date"]
        - pd.to_timedelta(
            pricing_history["date"].dt.dayofweek,
            unit="D",
        )
    )

    weekly_item = (
        pricing_history
        .groupby(
            [
                "item_id",
                "store_id",
                "week_start",
            ],
            as_index=False,
        )
        .agg(
            weekly_units=(
                "units_sold",
                "sum",
            ),
            weekly_price=(
                "sell_price",
                "mean",
            ),
        )
        .sort_values(
            [
                "item_id",
                "store_id",
                "week_start",
            ]
        )
        .reset_index(drop=True)
    )

    return weekly_item


def estimate_elasticity_observations(
    weekly_item: pd.DataFrame,
) -> pd.DataFrame:
    """
    Estimate observational week-over-week elasticity values.

    Elasticity approximation:
        percent demand change / percent price change

    Only price changes of at least 1% are used.
    Extreme observational estimates are clipped to [-5, 2], matching
    Notebook 06.
    """

    required_columns = [
        "item_id",
        "store_id",
        "week_start",
        "weekly_units",
        "weekly_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in weekly_item.columns
    ]

    if missing_columns:
        raise ValueError(
            "Weekly pricing data is missing columns: "
            f"{missing_columns}"
        )

    weekly_item = weekly_item.sort_values(
        [
            "item_id",
            "store_id",
            "week_start",
        ]
    ).copy()

    group_keys = [
        "item_id",
        "store_id",
    ]

    weekly_item["previous_price"] = (
        weekly_item
        .groupby(group_keys)["weekly_price"]
        .shift(1)
    )

    weekly_item["previous_units"] = (
        weekly_item
        .groupby(group_keys)["weekly_units"]
        .shift(1)
    )

    weekly_item["price_change_pct"] = (
        weekly_item["weekly_price"]
        / weekly_item["previous_price"]
        - 1
    )

    weekly_item["demand_change_pct"] = (
        weekly_item["weekly_units"]
        / weekly_item["previous_units"].replace(
            0,
            np.nan,
        )
        - 1
    )

    elasticity_observations = weekly_item.loc[
        weekly_item[
            "price_change_pct"
        ].abs() >= 0.01
    ].copy()

    elasticity_observations["elasticity"] = (
        elasticity_observations[
            "demand_change_pct"
        ]
        / elasticity_observations[
            "price_change_pct"
        ]
    )

    elasticity_observations = (
        elasticity_observations.loc[
            elasticity_observations[
                "elasticity"
            ]
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .notna()
        ]
        .copy()
    )

    elasticity_observations["elasticity"] = (
        elasticity_observations[
            "elasticity"
        ]
        .clip(-5, 2)
    )

    return elasticity_observations


def build_item_elasticity(
    elasticity_observations: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build one usable elasticity assumption for each item-store pair.

    Observed elasticity is used only when:
    - there are at least 3 usable observations
    - the median observed elasticity is negative

    Otherwise a fallback elasticity of -1.0 is used.

    Final usable elasticity is constrained to [-3.0, -0.2].
    """

    if elasticity_observations.empty:
        return pd.DataFrame(
            columns=[
                "item_id",
                "store_id",
                "estimated_elasticity",
                "elasticity_observations",
                "elasticity_source",
                "usable_elasticity",
            ]
        )

    item_elasticity = (
        elasticity_observations
        .groupby(
            [
                "item_id",
                "store_id",
            ],
            as_index=False,
        )
        .agg(
            estimated_elasticity=(
                "elasticity",
                "median",
            ),
            elasticity_observations=(
                "elasticity",
                "count",
            ),
        )
    )

    valid_observed_elasticity = (
        (
            item_elasticity[
                "elasticity_observations"
            ]
            >= MIN_ELASTICITY_OBSERVATIONS
        )
        & (
            item_elasticity[
                "estimated_elasticity"
            ] < 0
        )
    )

    item_elasticity[
        "elasticity_source"
    ] = np.where(
        valid_observed_elasticity,
        "Observed",
        "Fallback",
    )

    item_elasticity[
        "usable_elasticity"
    ] = np.where(
        valid_observed_elasticity,
        item_elasticity[
            "estimated_elasticity"
        ],
        FALLBACK_ELASTICITY,
    )

    item_elasticity[
        "usable_elasticity"
    ] = (
        item_elasticity[
            "usable_elasticity"
        ]
        .clip(-3.0, -0.2)
    )

    return item_elasticity


def estimate_item_elasticities(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convenience wrapper:
    daily feature history -> weekly history -> item elasticity table.
    """

    weekly_item = (
        build_weekly_price_history(
            feature_df
        )
    )

    elasticity_observations = (
        estimate_elasticity_observations(
            weekly_item
        )
    )

    return build_item_elasticity(
        elasticity_observations
    )


def validate_prediction_data(
    predictions_df: pd.DataFrame,
) -> None:
    """
    Validate forecast data before pricing.
    """

    required_columns = [
        "date",
        "item_id",
        "store_id",
        "prediction",
        "sell_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in predictions_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Prediction data is missing required pricing columns: "
            f"{missing_columns}"
        )

    if predictions_df.empty:
        raise ValueError(
            "Prediction data is empty."
        )

    if (
        predictions_df[
            "prediction"
        ] < 0
    ).any():
        raise ValueError(
            "Negative demand predictions were found."
        )


def create_pricing_base(
    predictions_df: pd.DataFrame,
    item_elasticity: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach observed/fallback elasticity assumptions to forecast rows.

    Rows without a valid positive price are excluded from pricing.
    """

    validate_prediction_data(
        predictions_df
    )

    pricing_base = predictions_df.copy()

    if not item_elasticity.empty:
        pricing_base = pricing_base.merge(
            item_elasticity[
                [
                    "item_id",
                    "store_id",
                    "usable_elasticity",
                    "elasticity_observations",
                    "elasticity_source",
                ]
            ],
            on=[
                "item_id",
                "store_id",
            ],
            how="left",
            validate="many_to_one",
        )
    else:
        pricing_base[
            "usable_elasticity"
        ] = np.nan

        pricing_base[
            "elasticity_observations"
        ] = np.nan

        pricing_base[
            "elasticity_source"
        ] = np.nan

    pricing_base[
        "usable_elasticity"
    ] = (
        pricing_base[
            "usable_elasticity"
        ]
        .fillna(
            FALLBACK_ELASTICITY
        )
    )

    pricing_base[
        "elasticity_observations"
    ] = (
        pricing_base[
            "elasticity_observations"
        ]
        .fillna(0)
        .astype(int)
    )

    pricing_base[
        "elasticity_source"
    ] = (
        pricing_base[
            "elasticity_source"
        ]
        .fillna("Fallback")
    )

    pricing_base = pricing_base.loc[
        pricing_base[
            "sell_price"
        ].notna()
        & (
            pricing_base[
                "sell_price"
            ] > 0
        )
    ].copy()

    return pricing_base


def estimate_scenario_demand(
    baseline_demand: float,
    current_price: float,
    candidate_price: float,
    elasticity: float,
) -> float:
    """
    Estimate demand under a candidate price using a constant-elasticity
    scenario model.

    scenario demand =
        baseline demand * (candidate price / current price) ** elasticity
    """

    if (
        baseline_demand < 0
        or current_price <= 0
        or candidate_price <= 0
    ):
        return np.nan

    relative_price = (
        candidate_price
        / current_price
    )

    scenario_demand = (
        baseline_demand
        * relative_price ** elasticity
    )

    return max(
        float(scenario_demand),
        0.0,
    )


def recommend_price_for_row(
    row: pd.Series,
) -> pd.Series:
    """
    Recommend the revenue-maximizing candidate price for one forecast row.

    Prices within 0.1% of the maximum expected revenue are treated as
    economically equivalent. Among those prices, the engine chooses the
    smallest absolute price change.
    """

    current_price = float(
        row["sell_price"]
    )

    baseline_demand = float(
        row["prediction"]
    )

    elasticity = float(
        row["usable_elasticity"]
    )

    scenarios = []

    for change_pct in PRICE_CHANGE_OPTIONS:

        candidate_price = max(
            current_price
            * (1 + change_pct),
            PRICE_FLOOR,
        )

        expected_demand = (
            estimate_scenario_demand(
                baseline_demand=baseline_demand,
                current_price=current_price,
                candidate_price=candidate_price,
                elasticity=elasticity,
            )
        )

        expected_revenue = (
            candidate_price
            * expected_demand
        )

        scenarios.append({
            "recommended_price": (
                candidate_price
            ),
            "recommended_change_pct": (
                float(change_pct)
            ),
            "expected_demand": (
                expected_demand
            ),
            "expected_revenue": (
                expected_revenue
            ),
        })

    scenario_df = pd.DataFrame(
        scenarios
    )

    max_revenue = (
        scenario_df[
            "expected_revenue"
        ].max()
    )

    revenue_tolerance = max(
        abs(max_revenue)
        * REVENUE_TOLERANCE_PCT,
        1e-9,
    )

    near_best = scenario_df.loc[
        scenario_df[
            "expected_revenue"
        ]
        >= max_revenue
        - revenue_tolerance
    ].copy()

    near_best[
        "absolute_price_change"
    ] = (
        near_best[
            "recommended_change_pct"
        ].abs()
    )

    best = near_best.loc[
        near_best[
            "absolute_price_change"
        ].idxmin()
    ]

    return best[
        [
            "recommended_price",
            "recommended_change_pct",
            "expected_demand",
            "expected_revenue",
        ]
    ]


def generate_recommendations(
    pricing_base: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate dynamic-pricing scenarios for every pricing-eligible row.
    """

    if pricing_base.empty:
        raise ValueError(
            "No pricing-eligible rows were found."
        )

    recommendations = (
        pricing_base.apply(
            recommend_price_for_row,
            axis=1,
        )
    )

    pricing_results = pd.concat(
        [
            pricing_base.reset_index(
                drop=True
            ),
            recommendations.reset_index(
                drop=True
            ),
        ],
        axis=1,
    )

    pricing_results[
        "current_expected_revenue"
    ] = (
        pricing_results[
            "sell_price"
        ]
        * pricing_results[
            "prediction"
        ]
    )

    pricing_results[
        "expected_revenue_lift"
    ] = (
        pricing_results[
            "expected_revenue"
        ]
        - pricing_results[
            "current_expected_revenue"
        ]
    )

    pricing_results[
        "expected_revenue_lift_pct"
    ] = (
        pricing_results[
            "expected_revenue_lift"
        ]
        / pricing_results[
            "current_expected_revenue"
        ].replace(
            0,
            np.nan,
        )
    )

    pricing_results[
        "pricing_action"
    ] = np.select(
        [
            pricing_results[
                "recommended_change_pct"
            ] < 0,
            pricing_results[
                "recommended_change_pct"
            ] > 0,
        ],
        [
            "Decrease",
            "Increase",
        ],
        default="Keep",
    )

    pricing_results[
        "recommendation_actionable"
    ] = (
        pricing_results[
            "expected_revenue_lift_pct"
        ]
        >= MIN_REVENUE_LIFT_PCT
    ) & (
        pricing_results[
            "prediction"
        ] > 0
    ) & (
        pricing_results[
            "sell_price"
        ] > 0
    )

    validate_pricing_results(
        pricing_results
    )

    return pricing_results


def validate_pricing_results(
    pricing_results: pd.DataFrame,
) -> None:
    """
    Validate production pricing guardrails.
    """

    if (
        pricing_results[
            "recommended_change_pct"
        ].abs()
        > 0.10 + 1e-12
    ).any():
        raise ValueError(
            "A recommended price exceeds the +/-10% pricing guardrail."
        )

    if (
        pricing_results[
            "recommended_price"
        ] <= 0
    ).any():
        raise ValueError(
            "A non-positive recommended price was found."
        )

    revenue_tolerance = np.maximum(
        pricing_results[
            "current_expected_revenue"
        ].abs()
        * REVENUE_TOLERANCE_PCT,
        1e-9,
    )

    materially_worse = (
        pricing_results[
            "expected_revenue"
        ]
        <
        pricing_results[
            "current_expected_revenue"
        ]
        - revenue_tolerance
    )

    if materially_worse.any():
        raise ValueError(
            "A recommendation is materially worse than "
            "the current-price scenario."
        )

    if (
        pricing_results[
            "expected_demand"
        ] < 0
    ).any():
        raise ValueError(
            "Negative scenario demand was found."
        )


def summarize_pricing(
    pricing_results: pd.DataFrame,
) -> dict:
    """
    Return a compact summary for CLI logging, FastAPI, or Streamlit.
    """

    action_counts = (
        pricing_results[
            "pricing_action"
        ]
        .value_counts()
    )

    total_rows = len(
        pricing_results
    )

    current_revenue = float(
        pricing_results[
            "current_expected_revenue"
        ].sum()
    )

    recommended_revenue = float(
        pricing_results[
            "expected_revenue"
        ].sum()
    )

    revenue_lift = (
        recommended_revenue
        - current_revenue
    )

    if current_revenue != 0:
        revenue_lift_pct = (
            revenue_lift
            / current_revenue
        )
    else:
        revenue_lift_pct = np.nan

    elasticity_counts = (
        pricing_results[
            "elasticity_source"
        ]
        .value_counts()
    )

    return {
        "rows": total_rows,
        "decrease_share": (
            action_counts.get(
                "Decrease",
                0,
            )
            / total_rows
        ),
        "keep_share": (
            action_counts.get(
                "Keep",
                0,
            )
            / total_rows
        ),
        "increase_share": (
            action_counts.get(
                "Increase",
                0,
            )
            / total_rows
        ),
        "actionable_rows": int(
            pricing_results[
                "recommendation_actionable"
            ].sum()
        ),
        "actionable_share": float(
            pricing_results[
                "recommendation_actionable"
            ].mean()
        ),
        "observed_elasticity_rows": int(
            elasticity_counts.get(
                "Observed",
                0,
            )
        ),
        "fallback_elasticity_rows": int(
            elasticity_counts.get(
                "Fallback",
                0,
            )
        ),
        "current_expected_revenue": (
            current_revenue
        ),
        "recommended_expected_revenue": (
            recommended_revenue
        ),
        "simulated_revenue_lift": (
            revenue_lift
        ),
        "simulated_revenue_lift_pct": (
            float(
                revenue_lift_pct
            )
            if np.isfinite(
                revenue_lift_pct
            )
            else None
        ),
    }


def recommend_prices(
    feature_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Main reusable pricing function.

    Historical feature data -> elasticity assumptions
    Forecast rows -> pricing base
    Pricing base -> guarded price recommendations
    """

    item_elasticity = (
        estimate_item_elasticities(
            feature_df
        )
    )

    pricing_base = (
        create_pricing_base(
            predictions_df=predictions_df,
            item_elasticity=item_elasticity,
        )
    )

    return generate_recommendations(
        pricing_base
    )


def load_pricing_inputs(
    feature_file: Path,
    predictions_file: Path,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Load processed feature history and forecast output.
    """

    feature_file = Path(
        feature_file
    )

    predictions_file = Path(
        predictions_file
    )

    if not feature_file.exists():
        raise FileNotFoundError(
            f"Feature file not found: {feature_file}"
        )

    if not predictions_file.exists():
        raise FileNotFoundError(
            f"Predictions file not found: {predictions_file}"
        )

    feature_df = pd.read_csv(
        feature_file,
        parse_dates=["date"],
        low_memory=False,
    )

    predictions_df = pd.read_csv(
        predictions_file,
        parse_dates=["date"],
        low_memory=False,
    )

    return (
        feature_df,
        predictions_df,
    )


def save_pricing_recommendations(
    pricing_results: pd.DataFrame,
    project_root: Path,
    filename: str = "pricing_recommendations.csv",
) -> Path:
    """
    Save pricing recommendations for downstream API/dashboard use.
    """

    project_root = Path(
        project_root
    )

    output_dir = (
        project_root
        / "outputs"
        / "pricing"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / filename
    )

    pricing_results.to_csv(
        output_file,
        index=False,
    )

    return output_file


def run_pricing(
    project_root: Path,
    feature_file: Path,
    predictions_file: Path,
    save_output: bool = True,
    output_filename: str = "pricing_recommendations.csv",
) -> pd.DataFrame:
    """
    Convenience batch workflow:

    feature history + demand predictions
        -> elasticity assumptions
        -> candidate-price scenarios
        -> guarded recommendations
        -> optional CSV output
    """

    project_root = Path(
        project_root
    )

    (
        feature_df,
        predictions_df,
    ) = load_pricing_inputs(
        feature_file=feature_file,
        predictions_file=predictions_file,
    )

    pricing_results = (
        recommend_prices(
            feature_df=feature_df,
            predictions_df=predictions_df,
        )
    )

    if save_output:
        output_file = (
            save_pricing_recommendations(
                pricing_results=pricing_results,
                project_root=project_root,
                filename=output_filename,
            )
        )

        print(
            "Saved:",
            output_file,
        )

    summary = summarize_pricing(
        pricing_results
    )

    print(
        "Pricing rows:",
        f"{summary['rows']:,}",
    )

    print(
        "Actions:",
        f"Decrease {summary['decrease_share']:.2%} |",
        f"Keep {summary['keep_share']:.2%} |",
        f"Increase {summary['increase_share']:.2%}",
    )

    print(
        "Actionable:",
        f"{summary['actionable_rows']:,}",
        f"({summary['actionable_share']:.2%})",
    )

    print(
        "Elasticity source:",
        f"Observed {summary['observed_elasticity_rows']:,} |",
        f"Fallback {summary['fallback_elasticity_rows']:,}",
    )

    print(
        "Simulated expected revenue:",
        f"${summary['current_expected_revenue']:,.2f}",
        "->",
        f"${summary['recommended_expected_revenue']:,.2f}",
    )

    print(
        "Simulated expected revenue lift:",
        f"${summary['simulated_revenue_lift']:,.2f}",
        f"({summary['simulated_revenue_lift_pct']:.2%})",
    )

    print(
        "PASS: price guardrails"
    )

    print(
        "PASS: positive recommended prices"
    )

    print(
        "PASS: no materially worse revenue recommendations"
    )

    print(
        "PASS: dynamic pricing complete"
    )

    return pricing_results


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

    PREDICTIONS_FILE = (
        PROJECT_ROOT
        / "outputs"
        / "forecasting"
        / "latest_predictions.csv"
    )

    run_pricing(
        project_root=PROJECT_ROOT,
        feature_file=FEATURE_FILE,
        predictions_file=PREDICTIONS_FILE,
        save_output=True,
    )
