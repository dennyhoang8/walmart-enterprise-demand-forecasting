# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform the price DataFrame.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM PRICE DATA
# Take the raw M5 sell price data
# and prepare it for fact_prices.
# ================================

def transform_prices(
    prices: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw M5 price data into the
    warehouse-ready fact_prices format.
    """


    # ================================
    # 3. DEFINE NEEDED COLUMNS
    # Create a list of the exact columns
    # that fact_prices needs.
    # ================================

    expected_columns = [
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price",
    ]


    # ================================
    # 4. KEEP ONLY NEEDED COLUMNS
    # Select the expected columns from the
    # raw price DataFrame and make a copy.
    # ================================

    prices = prices[
        expected_columns
    ].copy()


    # ================================
    # 5. RETURN TRANSFORMED DATA
    # Give the finished price DataFrame
    # back to the code that called this function.
    # ================================

    return prices