
# ================================
# 1. IMPORT TOOLS
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM ECONOMIC DATA
# Prepare FRED data for PostgreSQL.
# ================================

def transform_economic(
    economic_data: pd.DataFrame,
) -> pd.DataFrame:

    # ================================
    # 3. DEFINE REQUIRED COLUMNS
    # ================================

    required_columns = [
        "date",
        "value",
        "series_id",
    ]

    # ================================
    # 4. CHECK REQUIRED COLUMNS
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
    # 5. COPY REQUIRED COLUMNS
    # ================================

    economic_data = economic_data[required_columns].copy()

    # ================================
    # 6. CONVERT VALUE TO NUMERIC
    # ================================

    economic_data["value"] = pd.to_numeric(
        economic_data["value"],
        errors="raise",
    )

    # ================================
    # 7. RENAME DATE COLUMN
    # ================================

    economic_data = economic_data.rename(
        columns={
            "date": "observation_date",
        }
    )

    # ================================
    # 8. CONVERT DATE FORMAT
    # ================================

    economic_data["observation_date"] = pd.to_datetime(
        economic_data["observation_date"],
        errors="raise",
    ).dt.date

    # ================================
    # 9. KEEP FINAL COLUMNS
    # ================================

    expected_columns = [
        "series_id",
        "observation_date",
        "value",
    ]

    economic_data = economic_data[expected_columns].copy()

    # ================================
    # 10. CHECK MISSING VALUES
    # ================================

    if economic_data.isnull().any().any():
        raise ValueError(
            "Economic data contains missing values."
        )

    # ================================
    # 11. CHECK DUPLICATE RECORDS
    # Each series should have one value per date.
    # ================================

    duplicate_count = economic_data.duplicated(
        subset=["series_id", "observation_date"]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} duplicate economic records."
        )

    # ================================
    # 12. RETURN TRANSFORMED DATA
    # ================================

    return economic_data
