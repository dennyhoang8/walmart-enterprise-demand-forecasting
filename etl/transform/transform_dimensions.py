# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform DataFrames.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM PRODUCT DATA
# Take product information from the
# raw M5 sales DataFrame and prepare
# one row per product for dim_product.
# ================================

def transform_products(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 product information into
    the warehouse-ready dim_product format.
    """

    required_columns = [
        "item_id",
        "dept_id",
        "cat_id",
    ]

    # Make sure the source contains the columns
    # required to build dim_product.
    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing product columns: {missing_columns}"
        )

    # Sales contains repeated product information
    # because the same product appears across stores.
    #
    # Keep only the product hierarchy columns and
    # collapse those repeated rows into one row
    # per unique product.
    products = (
        sales[required_columns]
        .drop_duplicates()
        .sort_values("item_id")
        .reset_index(drop=True)
    )

    return products


# ================================
# 3. TRANSFORM STORE DATA
# Take store information from the
# raw M5 sales DataFrame and prepare
# one row per store for dim_store.
# ================================

def transform_stores(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 store information into
    the warehouse-ready dim_store format.
    """

    required_columns = [
        "store_id",
        "state_id",
    ]

    # Make sure the source contains the columns
    # required to build dim_store.
    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing store columns: {missing_columns}"
        )

    # Sales contains repeated store information
    # because many products belong to the same store.
    #
    # Keep only the store columns and collapse
    # those repeated rows into one row per store.
    stores = (
        sales[required_columns]
        .drop_duplicates()
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    return stores


# ================================
# 4. TRANSFORM CALENDAR DATA
# Take the raw M5 calendar DataFrame
# and prepare it for dim_calendar.
# ================================

def transform_calendar(
    calendar: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform the raw M5 calendar into
    the warehouse-ready dim_calendar format.
    """

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

    # Confirm the calendar schema before
    # applying transformations.
    missing_columns = [
        column
        for column in required_columns
        if column not in calendar.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing calendar columns: {missing_columns}"
        )

    # Work on a copy so the original
    # DataFrame is not modified.
    calendar = calendar.copy()

    # Notebook 01 showed that date is loaded
    # as text, so convert it to a real date.
    calendar["date"] = pd.to_datetime(
        calendar["date"],
        errors="raise",
    ).dt.date

    # Rename SNAP columns so they match
    # PostgreSQL naming conventions.
    calendar = calendar.rename(
        columns={
            "snap_CA": "snap_ca",
            "snap_TX": "snap_tx",
            "snap_WI": "snap_wi",
        }
    )

    # SNAP is stored as 0/1 in the raw source.
    # Convert those indicators to booleans.
    for column in [
        "snap_ca",
        "snap_tx",
        "snap_wi",
    ]:
        calendar[column] = calendar[column].astype(bool)

    # Important:
    # event_name/event_type nulls are expected
    # and should remain null. They represent
    # dates with no corresponding special event.

    return calendar