"""
Reusable feature engineering for the Walmart M5 forecasting project.

This module moves the finalized logic from Notebook 03 into reusable
Python functions so notebooks, APIs, batch jobs, and Airflow can all
build the same model-ready features.

Important:
- Historical demand features only use prior observations.
- Rolling features are shifted before calculation.
- Economic observations are delayed by one month before joining.
- Missing sell prices are allowed only when units_sold == 0.
"""

from pathlib import Path

import numpy as np
import pandas as pd


LAGS = [1, 7, 14, 28]
ROLLING_WINDOWS = [7, 28]

FINAL_COLUMNS = [
    "date",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
    "units_sold",

    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",

    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_28",
    "rolling_std_28",
    "zero_sales_share_28",

    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "year",
    "is_weekend",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",

    "event_name_1",
    "event_type_1",
    "event_name_2",
    "event_type_2",
    "has_any_event",

    "holiday_name",
    "is_us_holiday",
    "snap",

    "sell_price",
    "price_available",
    "previous_sell_price",
    "price_change",
    "price_change_pct",

    "temperature_max",
    "temperature_min",
    "precipitation",
    "snowfall",
    "wind_speed_max",

    "CPIAUCSL",
    "UNRATE",
    "FEDFUNDS",
]


def load_source_data(project_root: Path) -> dict[str, pd.DataFrame]:
    """
    Load the same raw and external source files used by Notebook 03.
    """

    project_root = Path(project_root)

    raw_dir = project_root / "data" / "raw"
    external_dir = project_root / "data" / "external"

    calendar = pd.read_csv(
        raw_dir / "calendar.csv"
    )

    prices = pd.read_csv(
        raw_dir / "sell_prices.csv"
    )

    sales = pd.read_csv(
        raw_dir / "sales_train_evaluation.csv"
    )

    fred = pd.read_csv(
        external_dir / "fred_economic_data.csv"
    )

    holidays = pd.read_csv(
        external_dir / "us_holidays.csv"
    )

    weather = pd.read_csv(
        external_dir / "weather_history.csv"
    )

    calendar["date"] = pd.to_datetime(
        calendar["date"]
    )

    fred["date"] = pd.to_datetime(
        fred["date"]
    )

    holidays["date"] = pd.to_datetime(
        holidays["date"]
    )

    weather["time"] = pd.to_datetime(
        weather["time"]
    )

    return {
        "calendar": calendar,
        "prices": prices,
        "sales": sales,
        "fred": fred,
        "holidays": holidays,
        "weather": weather,
    }


def filter_store_sales(
    sales: pd.DataFrame,
    store_id: str,
    max_items: int | None = None,
) -> pd.DataFrame:
    """
    Keep one store and optionally limit the number of products.
    """

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()

    if max_items is not None:
        selected_items = (
            store_sales["item_id"]
            .drop_duplicates()
            .sort_values()
            .head(max_items)
        )

        store_sales = store_sales.loc[
            store_sales["item_id"].isin(
                selected_items
            )
        ].copy()

    if store_sales.empty:
        raise ValueError(
            f"No sales rows found for store_id={store_id}."
        )

    return store_sales


def reshape_sales(
    store_sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the M5 wide d_1...d_n structure into long format.
    """

    id_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]

    sales_long = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )

    return sales_long


def attach_calendar(
    sales_long: pd.DataFrame,
    calendar: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach Walmart calendar, event, and SNAP information.
    """

    calendar_columns = [
        "d",
        "date",
        "wm_yr_wk",
        "weekday",
        "wday",
        "month",
        "year",
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    feature_df = sales_long.merge(
        calendar[calendar_columns],
        on="d",
        how="left",
        validate="many_to_one",
    )

    feature_df = (
        feature_df
        .sort_values(
            ["item_id", "store_id", "date"]
        )
        .reset_index(drop=True)
    )

    return feature_df


def validate_base_feature_table(
    feature_df: pd.DataFrame,
) -> None:
    """
    Validate the sales + calendar base table.
    """

    if feature_df["date"].isna().any():
        raise ValueError(
            "Some sales rows did not match a calendar date."
        )

    if feature_df["units_sold"].isna().any():
        raise ValueError(
            "Missing sales values were found."
        )

    if (feature_df["units_sold"] < 0).any():
        raise ValueError(
            "Negative sales values were found."
        )

    duplicate_keys = feature_df.duplicated(
        subset=[
            "date",
            "item_id",
            "store_id",
        ]
    ).sum()

    if duplicate_keys > 0:
        raise ValueError(
            f"Found {duplicate_keys:,} duplicate "
            "date-item-store rows."
        )


def add_lag_features(
    feature_df: pd.DataFrame,
    lags: list[int] = LAGS,
) -> pd.DataFrame:
    """
    Add prior-demand lag features.
    """

    feature_df = feature_df.copy()

    series_key = [
        "item_id",
        "store_id",
    ]

    for lag in lags:
        feature_df[f"lag_{lag}"] = (
            feature_df
            .groupby(series_key)["units_sold"]
            .shift(lag)
        )

    return feature_df


def add_rolling_features(
    feature_df: pd.DataFrame,
    rolling_windows: list[int] = ROLLING_WINDOWS,
) -> pd.DataFrame:
    """
    Add leakage-safe rolling mean and rolling standard deviation features.

    Sales are shifted by one day before rolling calculations so the
    current day's target is never included in its own features.
    """

    feature_df = feature_df.copy()

    shifted_sales = (
        feature_df
        .groupby(
            ["item_id", "store_id"]
        )["units_sold"]
        .shift(1)
    )

    for window in rolling_windows:
        grouped_shifted = (
            shifted_sales.groupby(
                [
                    feature_df["item_id"],
                    feature_df["store_id"],
                ]
            )
        )

        feature_df[
            f"rolling_mean_{window}"
        ] = (
            grouped_shifted
            .rolling(
                window,
                min_periods=1,
            )
            .mean()
            .reset_index(
                level=[0, 1],
                drop=True,
            )
        )

        feature_df[
            f"rolling_std_{window}"
        ] = (
            grouped_shifted
            .rolling(
                window,
                min_periods=2,
            )
            .std()
            .reset_index(
                level=[0, 1],
                drop=True,
            )
        )

    return feature_df


def add_zero_sales_feature(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add the fraction of the previous 28 days with zero sales.
    """

    feature_df = feature_df.copy()

    zero_indicator = (
        feature_df["units_sold"]
        .eq(0)
        .astype(int)
    )

    shifted_zero = zero_indicator.groupby(
        [
            feature_df["item_id"],
            feature_df["store_id"],
        ]
    ).shift(1)

    feature_df["zero_sales_share_28"] = (
        shifted_zero
        .groupby(
            [
                feature_df["item_id"],
                feature_df["store_id"],
            ]
        )
        .rolling(
            28,
            min_periods=1,
        )
        .mean()
        .reset_index(
            level=[0, 1],
            drop=True,
        )
    )

    return feature_df


def add_calendar_features(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add standard calendar and seasonality features.
    """

    feature_df = feature_df.copy()

    feature_df["day_of_week"] = (
        feature_df["date"].dt.dayofweek
    )

    feature_df["day_of_month"] = (
        feature_df["date"].dt.day
    )

    feature_df["week_of_year"] = (
        feature_df["date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    feature_df["month"] = (
        feature_df["date"].dt.month
    )

    feature_df["year"] = (
        feature_df["date"].dt.year
    )

    feature_df["is_weekend"] = (
        feature_df["day_of_week"] >= 5
    ).astype(int)

    return feature_df


def add_event_features(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add general Walmart event indicators.
    """

    feature_df = feature_df.copy()

    feature_df["has_event_1"] = (
        feature_df["event_name_1"]
        .notna()
        .astype(int)
    )

    feature_df["has_event_2"] = (
        feature_df["event_name_2"]
        .notna()
        .astype(int)
    )

    feature_df["has_any_event"] = (
        feature_df["has_event_1"]
        | feature_df["has_event_2"]
    ).astype(int)

    return feature_df


def add_snap_feature(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert the state-specific SNAP field into one general 'snap' feature.
    """

    feature_df = feature_df.copy()

    state_ids = (
        feature_df["state_id"]
        .dropna()
        .unique()
    )

    if len(state_ids) != 1:
        raise ValueError(
            "Expected exactly one state in the store-level "
            "feature dataset."
        )

    state_id = state_ids[0]

    snap_column_map = {
        "CA": "snap_CA",
        "TX": "snap_TX",
        "WI": "snap_WI",
    }

    if state_id not in snap_column_map:
        raise ValueError(
            f"Unsupported state_id for SNAP: {state_id}"
        )

    snap_column = snap_column_map[
        state_id
    ]

    feature_df["snap"] = (
        feature_df[snap_column]
        .astype(int)
    )

    return feature_df


def add_holiday_features(
    feature_df: pd.DataFrame,
    holidays: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach U.S. holiday names and a binary holiday indicator.
    """

    holiday_lookup = holidays[
        [
            "date",
            "holiday_name",
        ]
    ].copy()

    feature_df = feature_df.merge(
        holiday_lookup,
        on="date",
        how="left",
        validate="many_to_one",
    )

    feature_df["is_us_holiday"] = (
        feature_df["holiday_name"]
        .notna()
        .astype(int)
    )

    return feature_df


def add_price_features(
    feature_df: pd.DataFrame,
    prices: pd.DataFrame,
    store_id: str,
    max_items: int | None = None,
) -> pd.DataFrame:
    """
    Add current price, prior weekly price, and price-change features.
    """

    store_prices = prices.loc[
        prices["store_id"] == store_id
    ].copy()

    if max_items is not None:
        store_prices = store_prices.loc[
            store_prices["item_id"].isin(
                feature_df[
                    "item_id"
                ].unique()
            )
        ].copy()

    store_prices = (
        store_prices
        .sort_values(
            [
                "store_id",
                "item_id",
                "wm_yr_wk",
            ]
        )
    )

    store_prices[
        "previous_sell_price"
    ] = (
        store_prices
        .groupby(
            [
                "store_id",
                "item_id",
            ]
        )["sell_price"]
        .shift(1)
    )

    store_prices[
        "price_change"
    ] = (
        store_prices["sell_price"]
        - store_prices[
            "previous_sell_price"
        ]
    )

    store_prices[
        "price_change_pct"
    ] = (
        store_prices["price_change"]
        / store_prices[
            "previous_sell_price"
        ]
    )

    price_features = store_prices[
        [
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price",
            "previous_sell_price",
            "price_change",
            "price_change_pct",
        ]
    ].copy()

    feature_df = feature_df.merge(
        price_features,
        on=[
            "store_id",
            "item_id",
            "wm_yr_wk",
        ],
        how="left",
        validate="many_to_one",
    )

    feature_df["price_available"] = (
        feature_df["sell_price"]
        .notna()
        .astype(int)
    )

    return feature_df


def add_weather_features(
    feature_df: pd.DataFrame,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join daily weather by date + state_id.
    """

    weather_features = (
        weather.rename(
            columns={
                "time": "date",
                "temperature_2m_max": "temperature_max",
                "temperature_2m_min": "temperature_min",
                "precipitation_sum": "precipitation",
                "snowfall_sum": "snowfall",
                "wind_speed_10m_max": "wind_speed_max",
            }
        )[
            [
                "date",
                "state_id",
                "temperature_max",
                "temperature_min",
                "precipitation",
                "snowfall",
                "wind_speed_max",
            ]
        ]
        .copy()
    )

    feature_df = feature_df.merge(
        weather_features,
        on=[
            "date",
            "state_id",
        ],
        how="left",
        validate="many_to_one",
    )

    return feature_df


def add_economic_features(
    feature_df: pd.DataFrame,
    fred: pd.DataFrame,
) -> pd.DataFrame:
    """
    Pivot monthly FRED series and apply a one-month availability lag
    before joining to daily sales observations.
    """

    fred_wide = (
        fred
        .pivot(
            index="date",
            columns="series_id",
            values="value",
        )
        .sort_index()
        .reset_index()
    )

    fred_wide["available_date"] = (
        fred_wide["date"]
        + pd.offsets.MonthBegin(1)
    )

    fred_available = (
        fred_wide
        .drop(columns="date")
        .sort_values(
            "available_date"
        )
    )

    feature_df = (
        pd.merge_asof(
            feature_df.sort_values(
                "date"
            ),
            fred_available,
            left_on="date",
            right_on="available_date",
            direction="backward",
        )
        .sort_values(
            [
                "item_id",
                "store_id",
                "date",
            ]
        )
        .reset_index(drop=True)
    )

    return feature_df


def add_cyclical_features(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add sine/cosine encodings for weekday and month.
    """

    feature_df = feature_df.copy()

    feature_df["dow_sin"] = np.sin(
        2
        * np.pi
        * feature_df["day_of_week"]
        / 7
    )

    feature_df["dow_cos"] = np.cos(
        2
        * np.pi
        * feature_df["day_of_week"]
        / 7
    )

    feature_df["month_sin"] = np.sin(
        2
        * np.pi
        * feature_df["month"]
        / 12
    )

    feature_df["month_cos"] = np.cos(
        2
        * np.pi
        * feature_df["month"]
        / 12
    )

    return feature_df


def select_final_columns(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep the finalized Notebook 03 feature columns.
    """

    missing_columns = [
        column
        for column in FINAL_COLUMNS
        if column not in feature_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required final columns: "
            f"{missing_columns}"
        )

    return feature_df[
        FINAL_COLUMNS
    ].copy()


def validate_missing_prices(
    model_features: pd.DataFrame,
) -> None:
    """
    Missing sell prices are acceptable only on zero-sales rows.
    """

    missing_price_sales = (
        model_features.loc[
            model_features[
                "sell_price"
            ].isna(),
            "units_sold",
        ]
    )

    if (
        missing_price_sales > 0
    ).any():
        raise ValueError(
            "Positive sales were found on rows with missing "
            "sell_price. Investigate the price join."
        )


def create_model_ready_dataset(
    model_features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only rows with a complete 28-day lag history.
    """

    model_ready = (
        model_features.loc[
            model_features[
                "lag_28"
            ].notna()
        ]
        .copy()
    )

    model_ready = (
        model_ready
        .sort_values(
            [
                "date",
                "store_id",
                "item_id",
            ]
        )
        .reset_index(drop=True)
    )

    return model_ready


def validate_final_features(
    model_ready: pd.DataFrame,
) -> None:
    """
    Final feature-table validation.
    """

    duplicate_count = (
        model_ready.duplicated(
            subset=[
                "date",
                "item_id",
                "store_id",
            ]
        ).sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count:,} duplicate feature keys."
        )

    if (
        model_ready["units_sold"] < 0
    ).any():
        raise ValueError(
            "Negative target values found."
        )

    if not (
        model_ready["lag_28"]
        .notna()
        .all()
    ):
        raise ValueError(
            "Model-ready data still contains missing lag_28 values."
        )


def build_features(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    prices: pd.DataFrame,
    fred: pd.DataFrame,
    holidays: pd.DataFrame,
    weather: pd.DataFrame,
    store_id: str,
    max_items: int | None = None,
) -> pd.DataFrame:
    """
    Build the complete model-ready feature dataset for one store.

    This is the main function that the forecasting pipeline,
    API, or Airflow task should call.
    """

    store_sales = filter_store_sales(
        sales=sales,
        store_id=store_id,
        max_items=max_items,
    )

    sales_long = reshape_sales(
        store_sales
    )

    feature_df = attach_calendar(
        sales_long=sales_long,
        calendar=calendar,
    )

    validate_base_feature_table(
        feature_df
    )

    feature_df = add_lag_features(
        feature_df
    )

    feature_df = add_rolling_features(
        feature_df
    )

    feature_df = add_zero_sales_feature(
        feature_df
    )

    feature_df = add_calendar_features(
        feature_df
    )

    feature_df = add_event_features(
        feature_df
    )

    feature_df = add_snap_feature(
        feature_df
    )

    feature_df = add_holiday_features(
        feature_df=feature_df,
        holidays=holidays,
    )

    feature_df = add_price_features(
        feature_df=feature_df,
        prices=prices,
        store_id=store_id,
        max_items=max_items,
    )

    feature_df = add_weather_features(
        feature_df=feature_df,
        weather=weather,
    )

    feature_df = add_economic_features(
        feature_df=feature_df,
        fred=fred,
    )

    feature_df = add_cyclical_features(
        feature_df
    )

    model_features = (
        select_final_columns(
            feature_df
        )
    )

    validate_missing_prices(
        model_features
    )

    model_ready = (
        create_model_ready_dataset(
            model_features
        )
    )

    validate_final_features(
        model_ready
    )

    return model_ready


def save_features(
    feature_df: pd.DataFrame,
    project_root: Path,
    store_id: str,
    max_items: int | None = None,
) -> Path:
    """
    Save the model-ready feature table using the same naming
    convention as Notebook 03.
    """

    project_root = Path(
        project_root
    )

    processed_dir = (
        project_root
        / "data"
        / "processed"
    )

    processed_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    item_suffix = (
        "all_items"
        if max_items is None
        else f"{max_items}_items"
    )

    output_file = (
        processed_dir
        / f"features_{store_id}_{item_suffix}.csv"
    )

    feature_df.to_csv(
        output_file,
        index=False,
    )

    return output_file


def build_features_from_files(
    project_root: Path,
    store_id: str,
    max_items: int | None = None,
    save_output: bool = True,
) -> pd.DataFrame:
    """
    Convenience function:
    load source files -> build features -> optionally save output.
    """

    datasets = load_source_data(
        project_root
    )

    model_ready = build_features(
        sales=datasets["sales"],
        calendar=datasets["calendar"],
        prices=datasets["prices"],
        fred=datasets["fred"],
        holidays=datasets["holidays"],
        weather=datasets["weather"],
        store_id=store_id,
        max_items=max_items,
    )

    if save_output:
        output_file = save_features(
            feature_df=model_ready,
            project_root=project_root,
            store_id=store_id,
            max_items=max_items,
        )

        print(
            "Saved:",
            output_file,
        )

    print(
        "Feature shape:",
        model_ready.shape,
    )

    print(
        "PASS: feature engineering complete"
    )

    return model_ready


if __name__ == "__main__":

    # Development defaults matching finalized Notebook 03.
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    STORE_ID = "CA_1"
    MAX_ITEMS = 200

    build_features_from_files(
        project_root=PROJECT_ROOT,
        store_id=STORE_ID,
        max_items=MAX_ITEMS,
        save_output=True,
    )