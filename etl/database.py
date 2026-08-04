from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    connection_string = (
        "postgresql+psycopg2://postgres:Donald1!"
        "@localhost:5432/walmart_forecasting"
    )

    return create_engine(connection_string)