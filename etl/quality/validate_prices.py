from etl.database import get_engine
from sqlalchemy import text


def validate_prices() -> None:
    engine = get_engine()

    checks = {
        "negative_or_zero_prices": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE sell_price <= 0;
        """,

        "duplicate_price_keys": """
            SELECT COUNT(*)
            FROM (
                SELECT store_id, item_id, wm_yr_wk
                FROM fact_prices
                GROUP BY store_id, item_id, wm_yr_wk
                HAVING COUNT(*) > 1
            ) x;
        """,

        "missing_price_keys": """
            SELECT COUNT(*)
            FROM fact_prices
            WHERE store_id IS NULL
               OR item_id IS NULL
               OR wm_yr_wk IS NULL;
        """
    }

    with engine.connect() as connection:
        for name, sql in checks.items():
            result = connection.execute(text(sql)).scalar()

            if result != 0:
                raise ValueError(f"{name} failed: {result}")

            print(f"PASS: {name}")


if __name__ == "__main__":
    validate_prices()