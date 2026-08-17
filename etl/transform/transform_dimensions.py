import pandas as pd


def transform_products(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 product information into
    the warehouse-ready dim_product format.
    """

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

    return products


def transform_stores(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 store information into
    the warehouse-ready dim_store format.
    """

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

    return stores


def transform_calendar(
    calendar: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform the raw M5 calendar into
    the warehouse-ready dim_calendar format.
    """

    calendar = calendar.copy()

    calendar["date"] = pd.to_datetime(
        calendar["date"]
    ).dt.date

    calendar = calendar.rename(
        columns={
            "snap_CA": "snap_ca",
            "snap_TX": "snap_tx",
            "snap_WI": "snap_wi",
        }
    )

    for column in [
        "snap_ca",
        "snap_tx",
        "snap_wi",
    ]:
        calendar[column] = calendar[column].astype(bool)

    return calendar