import pandas as pd


def transform_sales(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> pd.DataFrame:
    """
    Transform M5 sales data from wide format into
    warehouse-ready long format for one store.
    """

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()

    id_columns = [
        "item_id",
        "store_id",
    ]

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )

    long_sales = long_sales.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )

    long_sales["date"] = pd.to_datetime(
        long_sales["date"]
    ).dt.date

    fact_sales = long_sales[
        [
            "date",
            "item_id",
            "store_id",
            "units_sold",
        ]
    ].copy()

    return fact_sales