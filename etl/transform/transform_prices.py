import pandas as pd


def transform_prices(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 price data into the
    warehouse-ready fact_prices format.
    """

    expected_columns = [
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price",
    ]

    prices = prices[
        expected_columns
    ].copy()

    return prices