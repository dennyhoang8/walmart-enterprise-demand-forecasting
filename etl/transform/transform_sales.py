# ================================
# 1. IMPORT TOOLS
# Load Pandas for transforming data.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM SALES DATA
# Create the transformation function.
# sales, calendar, and store_id will receive
# the actual data later when this function is called.
# ================================

def transform_sales(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> pd.DataFrame:


    # ================================
    # 3. CHECK REQUIRED SALES COLUMNS
    # Make sure item_id and store_id exist.
    # Stop with an error if either is missing.
    # ================================

    required_sales_columns = [
        "item_id",
        "store_id",
    ]

    missing_sales_columns = [
        column
        for column in required_sales_columns
        if column not in sales.columns
    ]

    if missing_sales_columns:
        raise ValueError(
            f"Missing sales columns: {missing_sales_columns}"
        )


    # ================================
    # 4. CHECK REQUIRED CALENDAR COLUMNS
    # Make sure d and date exist in calendar data.
    # ================================

    required_calendar_columns = [
        "d",
        "date",
    ]

    missing_calendar_columns = [
        column
        for column in required_calendar_columns
        if column not in calendar.columns
    ]

    if missing_calendar_columns:
        raise ValueError(
            f"Missing calendar columns: {missing_calendar_columns}"
        )


    # ================================
    # 5. FILTER TO ONE STORE
    # Keep only sales for the store being processed.
    # Example: CA_1
    # ================================

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()

    if store_sales.empty:
        raise ValueError(
            f"No sales data found for store_id: {store_id}"
        )


    # ================================
    # 6. DEFINE ID COLUMNS
    # Keep item_id and store_id as identifiers
    # when reshaping the data.
    # ================================

    id_columns = [
        "item_id",
        "store_id",
    ]


    # ================================
    # 7. FIND DAY COLUMNS
    # Find M5 columns such as:
    # d_1, d_2, d_3, etc.
    # ================================

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "No M5 day columns were found."
        )


    # ================================
    # 8. RESHAPE WIDE TO LONG
    # Turn the d_ columns into rows.
    #
    # Creates:
    # d = day ID
    # units_sold = sales amount
    # ================================

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )


    # ================================
    # 9. CONVERT SALES TO NUMERIC
    # Make sure units_sold contains numbers.
    # ================================

    long_sales["units_sold"] = pd.to_numeric(
        long_sales["units_sold"],
        errors="raise",
    )


    # ================================
    # 10. ATTACH REAL DATES
    # Match d_1, d_2, etc. to their
    # actual dates from calendar.csv.
    # ================================

    calendar_lookup = calendar[
        [
            "d",
            "date",
        ]
    ].copy()

    long_sales = long_sales.merge(
        calendar_lookup,
        on="d",
        how="left",
        validate="many_to_one",
    )


    # ================================
    # 11. CHECK DATE MATCHES
    # Stop if any sales day could not
    # be matched to a real date.
    # ================================

    missing_dates = long_sales["date"].isna().sum()

    if missing_dates > 0:
        raise ValueError(
            f"{missing_dates} sales rows did not "
            "match a calendar date."
        )


    # ================================
    # 12. CONVERT DATE FORMAT
    # Convert date into proper date values.
    # ================================

    long_sales["date"] = pd.to_datetime(
        long_sales["date"],
        errors="raise",
    ).dt.date


    # ================================
    # 13. BUILD FINAL FACT_SALES DATA
    # Keep only the columns needed
    # for the fact_sales database table.
    # ================================

    fact_sales = long_sales[
        [
            "date",
            "item_id",
            "store_id",
            "units_sold",
        ]
    ].copy()


    # ================================
    # 14. RETURN TRANSFORMED DATA
    # Send fact_sales back to load_sales.py.
    # ================================

    return fact_sales