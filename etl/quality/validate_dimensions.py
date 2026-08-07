from etl.database import get_engine
from sqlalchemy import text


def validate_dimensions() -> None:
    engine = get_engine()

    checks = {
        "dim_product_null_keys": """
            SELECT COUNT(*)
            FROM dim_product
            WHERE item_id IS NULL;
        """,

        "dim_store_null_keys": """
            SELECT COUNT(*)
            FROM dim_store
            WHERE store_id IS NULL;
        """,

        "dim_calendar_null_dates": """
            SELECT COUNT(*)
            FROM dim_calendar
            WHERE date IS NULL;
        """,

        "dim_product_duplicates": """
            SELECT COUNT(*)
            FROM (
                SELECT item_id
                FROM dim_product
                GROUP BY item_id
                HAVING COUNT(*) > 1
            ) x;
        """,

        "dim_store_duplicates": """
            SELECT COUNT(*)
            FROM (
                SELECT store_id
                FROM dim_store
                GROUP BY store_id
                HAVING COUNT(*) > 1
            ) x;
        """,
    }

    with engine.connect() as connection:
        for name, sql in checks.items():
            result = connection.execute(text(sql)).scalar()

            if result != 0:
                raise ValueError(f"{name} failed: {result}")

            print(f"PASS: {name}")


if __name__ == "__main__":
    validate_dimensions()