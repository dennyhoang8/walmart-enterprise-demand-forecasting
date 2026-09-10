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
    # 3. DEFINE REQUIRED COLUMNS
    # These columns must exist before
    # transformation can continue.
    # ================================

    required_columns = [
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price",
    ]


    # ================================
    # 4. CHECK REQUIRED COLUMNS
    # Stop early if the source schema changes
    # and an expected column is missing.
    # ================================

    missing_columns = [
        column
        for column in required_columns
        if column not in prices.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing price columns: {missing_columns}"
        )


    # ================================
    # 5. KEEP ONLY NEEDED COLUMNS
    # Select only the columns required
    # by fact_prices and make a copy.
    # ================================

    prices = prices[
        required_columns
    ].copy()


    # ================================
    # 6. CONVERT DATA TYPES
    # Make sure numeric warehouse fields
    # are stored using numeric types.
    # ================================

    prices["wm_yr_wk"] = pd.to_numeric(
        prices["wm_yr_wk"],
        errors="raise",
    ).astype("int64")

    prices["sell_price"] = pd.to_numeric(
        prices["sell_price"],
        errors="raise",
    )


    # ================================
    # 7. RETURN TRANSFORMED DATA
    # Give the finished price DataFrame
    # back to the code that called this function.
    # ================================

    return prices