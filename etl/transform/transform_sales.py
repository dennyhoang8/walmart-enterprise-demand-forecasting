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
    # 3. FILTER TO ONE STORE
    # Keep only the sales rows that belong
    # to the current store being processed.
    # ================================

    store_sales = sales.loc[
        sales["store_id"] == store_id
    ].copy()


    # ================================
    # 4. DEFINE ID COLUMNS
    # These columns identify the product and store
    # and should stay as columns during the melt.
    # ================================

    id_columns = [
        "item_id",
        "store_id",
    ]


    # ================================
    # 5. FIND DAY COLUMNS
    # Find every sales column whose name
    # starts with "d_", such as d_1, d_2, d_3...
    # ================================

    day_columns = [
        column
        for column in store_sales.columns
        if column.startswith("d_")
    ]


    # ================================
    # 6. RESHAPE WIDE DATA TO LONG DATA
    # Turn the many d_ columns into rows with
    # one "d" column and one "units_sold" column.
    # ================================

    long_sales = store_sales.melt(
        id_vars=id_columns,
        value_vars=day_columns,
        var_name="d",
        value_name="units_sold",
    )


    # ================================
    # 7. ATTACH REAL CALENDAR DATES
    # Match each d_ value to its real date
    # using the calendar DataFrame.
    # ================================

    long_sales = long_sales.merge(
        calendar,
        on="d",
        how="left",
        validate="many_to_one",
    )


    # ================================
    # 8. CONVERT DATE FORMAT
    # Convert the date column into
    # proper Python date values.
    # ================================

    long_sales["date"] = pd.to_datetime(
        long_sales["date"]
    ).dt.date


    # ================================
    # 9. BUILD FINAL FACT_SALES FORMAT
    # Keep only the columns needed
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
    # 10. RETURN TRANSFORMED SALES
    # Give the finished fact_sales DataFrame
    # back to the load script.
    # ================================

    return fact_sales