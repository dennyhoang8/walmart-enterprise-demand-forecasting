from etl.database import get_engine
from sqlalchemy import text


def validate_sales() -> None:
    engine = get_engine()

    checks = {
        "negative_sales": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE units_sold < 0;
        """,

        "missing_sales_keys": """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE date IS NULL
               OR item_id IS NULL
               OR store_id IS NULL;
        """,

        "duplicate_sales_keys": """
            SELECT COUNT(*)
            FROM (
                SELECT date, item_id, store_id
                FROM fact_sales
                GROUP BY date, item_id, store_id
                HAVING COUNT(*) > 1
            ) x;
        """
    }

    with engine.connect() as connection:
        for name, sql in checks.items():
            result = connection.execute(text(sql)).scalar()

            if result != 0:
                raise ValueError(f"{name} failed: {result}")

            print(f"PASS: {name}")


if __name__ == "__main__":
    validate_sales()