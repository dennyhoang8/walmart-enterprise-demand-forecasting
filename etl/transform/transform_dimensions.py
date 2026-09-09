# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform DataFrames.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM PRODUCT DATA
# Take raw product information from the sales
# DataFrame and prepare it for dim_product.
# ================================

def transform_products(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 product information into
    the warehouse-ready dim_product format.
    """

    # Keep only the product-related columns,
    # remove duplicate products,
    # sort products by item_id,
    # and reset the row numbers.
    products = (
        sales[
            [
                "item_id",
                "dept_id",
                "cat_id",
            ]
        ]
        .drop_duplicates()
        .sort_values("item_id")
        .reset_index(drop=True)
    )

    # Give the finished product DataFrame back.
    return products


# ================================
# 3. TRANSFORM STORE DATA
# Take raw store information from the sales
# DataFrame and prepare it for dim_store.
# ================================

def transform_stores(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 store information into
    the warehouse-ready dim_store format.
    """

    # Keep only the store-related columns,
    # remove duplicate stores,
    # sort stores by store_id,
    # and reset the row numbers.
    stores = (
        sales[
            [
                "store_id",
                "state_id",
            ]
        ]
        .drop_duplicates()
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    # Give the finished store DataFrame back.
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

    # Make a separate copy so we do not
    # accidentally change the original DataFrame.
    calendar = calendar.copy()

    # Convert the date column into
    # proper Python date values.
    calendar["date"] = pd.to_datetime(
        calendar["date"]
    ).dt.date

    # Rename the SNAP columns so their names
    # match the PostgreSQL table column names.
    calendar = calendar.rename(
        columns={
            "snap_CA": "snap_ca",
            "snap_TX": "snap_tx",
            "snap_WI": "snap_wi",
        }
    )

    # Loop through each SNAP column
    # and convert its values to True/False.
    for column in [
        "snap_ca",
        "snap_tx",
        "snap_wi",
    ]:
        calendar[column] = calendar[column].astype(bool)

    # Give the finished calendar DataFrame back.
    return calendar