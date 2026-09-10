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
    # 3. DEFINE REQUIRED COLUMNS
    # These columns must exist in the extracted
    # FRED data before transformation can continue.
    # ================================

    required_columns = [
        "date",
        "value",
        "series_id",
    ]


    # ================================
    # 4. CHECK REQUIRED COLUMNS
    # Stop early with a clear error if the
    # extracted FRED schema changes.
    # ================================

    missing_columns = [
        column
        for column in required_columns
        if column not in economic_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing economic columns: {missing_columns}"
        )


    # ================================
    # 5. COPY THE DATA
    # Work on a separate DataFrame so the
    # original extracted data is not modified.
    # ================================

    economic_data = economic_data.copy()


    # ================================
    # 6. CONVERT VALUE TO NUMERIC
    # Notebook 01 showed value is already numeric,
    # but this makes the transform more robust.
    # ================================

    economic_data["value"] = pd.to_numeric(
        economic_data["value"],
        errors="raise",
    )


    # ================================
    # 7. RENAME THE DATE COLUMN
    # Change "date" to "observation_date"
    # so it matches the database table.
    # ================================

    economic_data = economic_data.rename(
        columns={
            "date": "observation_date",
        }
    )


    # ================================
    # 8. CONVERT TO PROPER DATE FORMAT
    # Convert observation_date into real
    # date values instead of leaving it as text.
    # ================================

    economic_data["observation_date"] = pd.to_datetime(
        economic_data["observation_date"],
        errors="raise",
    ).dt.date


    # ================================
    # 9. KEEP ONLY NEEDED COLUMNS
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
    # 10. RETURN TRANSFORMED DATA
    # Give the finished economic DataFrame
    # back to the code that called this function.
    # ================================

    return economic_data