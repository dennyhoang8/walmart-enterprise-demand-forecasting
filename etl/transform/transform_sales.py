# ================================
# 1. IMPORT TOOLS
# Load Pandas so we can work with
# and transform the sales DataFrame.
# ================================

import pandas as pd


# ================================
# 2. TRANSFORM SALES DATA
# Take the raw M5 sales data for one store,
# reshape it from wide to long format,
# attach real dates, and prepare it for fact_sales.
# ================================

def transform_sales(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    store_id: str,
) -> pd.DataFrame:
    """
    Transform M5 sales data from wide format into
    warehouse-ready long format for one store.
    """


    # ================================
    # 3. CHECK REQUIRED SALES COLUMNS
    # These columns must exist before
    # the sales transformation can run.
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
    # We need d to match the M5 day columns
    # and date to obtain the real calendar date.
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
    # Keep only the sales rows that belong
    # to the current store being processed.
    # ================================

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()


    # Make sure the requested store exists.
    if store_sales.empty:
        raise ValueError(
            f"No sales data found for store_id: {store_id}"
        )


    # ================================
    # 6. DEFINE ID COLUMNS
    # These identify the product and store
    # and stay as columns during the melt.
    # ================================

    id_columns = [
        "item_id",
        "store_id",
    ]


    # ================================
    # 7. FIND DAY COLUMNS
    # Find every daily sales column such as
    # d_1, d_2, d_3, ..., d_1913.
    # ================================

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]


    # Make sure daily sales columns were found.
    if not day_columns:
        raise ValueError(
            "No M5 day columns were found."
        )


    # ================================
    # 8. RESHAPE WIDE DATA TO LONG DATA
    # Turn d_1, d_2, d_3... from separate
    # columns into rows.
    # ================================

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )


    # ================================
    # 9. CONVERT SALES TO NUMERIC
    # Notebook 01 showed historical sales
    # are numeric and non-negative.
    # ================================

    long_sales["units_sold"] = pd.to_numeric(
        long_sales["units_sold"],
        errors="raise",
    )


    # ================================
    # 10. ATTACH REAL CALENDAR DATES
    # Match each d_* identifier to the
    # corresponding real calendar date.
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
    # 11. CHECK CALENDAR MATCHES
    # Every sales day should successfully
    # match a calendar date.
    # ================================

    missing_dates = long_sales["date"].isna().sum()

    if missing_dates > 0:
        raise ValueError(
            f"{missing_dates} sales rows did not "
            "match a calendar date."
        )


    # ================================
    # 12. CONVERT DATE FORMAT
    # Convert date into proper Python
    # date values.
    # ================================

    long_sales["date"] = pd.to_datetime(
        long_sales["date"],
        errors="raise",
    ).dt.date


    # ================================
    # 13. BUILD FINAL FACT_SALES FORMAT
    # Keep only the columns required
    # by the fact_sales database table.
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
    # 14. RETURN TRANSFORMED SALES
    # Give the finished fact_sales DataFrame
    # back to the load script.
    # ================================

    return fact_sales