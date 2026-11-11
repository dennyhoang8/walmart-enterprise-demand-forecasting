
# ================================
# 1. IMPORT TOOLS
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM PRODUCT DATA
# Prepare one row per product.
# ================================

def transform_products(
    sales: pd.DataFrame,
) -> pd.DataFrame:

    # Define required columns.
    required_columns = [
        "item_id",
        "dept_id",
        "cat_id",
    ]

    # Check for missing columns.
    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing product columns: {missing_columns}"
        )

    # Select required columns and remove duplicates.
    products = (
        sales[required_columns]
        .drop_duplicates()
        .sort_values("item_id")
        .reset_index(drop=True)
    )

    # Check for missing values.
    if products.isnull().any().any():
        raise ValueError(
            "Product data contains missing values."
        )

    # Each product ID must appear only once.
    if products["item_id"].duplicated().any():
        raise ValueError(
            "Duplicate product IDs found."
        )

    return products


# ================================
# 3. TRANSFORM STORE DATA
# Prepare one row per store.
# ================================

def transform_stores(
    sales: pd.DataFrame,
) -> pd.DataFrame:

    # Define required columns.
    required_columns = [
        "store_id",
        "state_id",
    ]

    # Check for missing columns.
    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing store columns: {missing_columns}"
        )

    # Select required columns and remove duplicates.
    stores = (
        sales[required_columns]
        .drop_duplicates()
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    # Check for missing values.
    if stores.isnull().any().any():
        raise ValueError(
            "Store data contains missing values."
        )

    # Each store ID must appear only once.
    if stores["store_id"].duplicated().any():
        raise ValueError(
            "Duplicate store IDs found."
        )

    return stores


# ================================
# 4. TRANSFORM CALENDAR DATA
# Prepare M5 calendar for PostgreSQL.
# ================================

def transform_calendar(
    calendar: pd.DataFrame,
) -> pd.DataFrame:

    # Define required columns.
    required_columns = [
        "date",
        "wm_yr_wk",
        "weekday",
        "wday",
        "month",
        "year",
        "d",
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    # Check for missing columns.
    missing_columns = [
        column
        for column in required_columns
        if column not in calendar.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing calendar columns: {missing_columns}"
        )

    # Select required columns.
    calendar = calendar[required_columns].copy()

    # ================================
    # 5. CONVERT DATE FORMAT
    # ================================

    calendar["date"] = pd.to_datetime(
        calendar["date"],
        errors="raise",
    ).dt.date

    # ================================
    # 6. RENAME SNAP COLUMNS
    # ================================

    calendar = calendar.rename(
        columns={
            "snap_CA": "snap_ca",
            "snap_TX": "snap_tx",
            "snap_WI": "snap_wi",
        }
    )

    # ================================
    # 7. VALIDATE SNAP VALUES
    # SNAP indicators must be 0 or 1.
    # ================================

    snap_columns = [
        "snap_ca",
        "snap_tx",
        "snap_wi",
    ]

    for column in snap_columns:

        calendar[column] = pd.to_numeric(
            calendar[column],
            errors="raise",
        )

        if not calendar[column].isin([0, 1]).all():
            raise ValueError(
                f"Invalid SNAP values in {column}."
            )

        calendar[column] = calendar[column].astype(bool)

    # ================================
    # 8. VALIDATE REQUIRED VALUES
    # Event columns may contain nulls.
    # ================================

    required_non_null = [
        "date",
        "wm_yr_wk",
        "weekday",
        "wday",
        "month",
        "year",
        "d",
        "snap_ca",
        "snap_tx",
        "snap_wi",
    ]

    if calendar[required_non_null].isnull().any().any():
        raise ValueError(
            "Calendar contains missing required values."
        )

    # ================================
    # 9. CONVERT NUMERIC COLUMNS
    # ================================

    numeric_columns = [
        "wm_yr_wk",
        "wday",
        "month",
        "year",
    ]

    for column in numeric_columns:
        calendar[column] = pd.to_numeric(
            calendar[column],
            errors="raise",
        ).astype("int64")

    # ================================
    # 10. CHECK DUPLICATE CALENDAR KEYS
    # ================================

    if calendar["date"].duplicated().any():
        raise ValueError(
            "Duplicate calendar dates found."
        )

    if calendar["d"].duplicated().any():
        raise ValueError(
            "Duplicate calendar day IDs found."
        )

    # ================================
    # 11. RETURN TRANSFORMED DATA
    # ================================

    return calendar
