# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform the economic DataFrame.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM ECONOMIC DATA
# Take the extracted FRED economic data
# and prepare it for fact_economic_indicator.
# ================================

def transform_economic(
    economic_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw FRED economic data into the
    warehouse-ready fact_economic_indicator format.
    """


    # ================================
    # 3. RENAME THE DATE COLUMN
    # Change "date" to "observation_date"
    # so it matches the database table.
    # ================================

    economic_data = economic_data.rename(
        columns={
            "date": "observation_date",
        }
    )


    # ================================
    # 4. CONVERT TO PROPER DATE FORMAT
    # Convert observation_date into real
    # date values instead of leaving it as text.
    # ================================

    economic_data["observation_date"] = pd.to_datetime(
        economic_data["observation_date"]
    ).dt.date


    # ================================
    # 5. KEEP ONLY NEEDED COLUMNS
    # Select only the columns that belong
    # in fact_economic_indicator.
    # ================================

    economic_data = economic_data[
        [
            "series_id",
            "observation_date",
            "value",
        ]
    ].copy()


    # ================================
    # 6. RETURN TRANSFORMED DATA
    # Give the finished economic DataFrame
    # back to the code that called this function.
    # ================================

    return economic_data