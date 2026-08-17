import pandas as pd


def transform_economic(
    economic_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform raw FRED economic data into the
    warehouse-ready fact_economic_indicator format.
    """

    economic_data = economic_data.rename(
        columns={
            "date": "observation_date",
        }
    )

    economic_data["observation_date"] = pd.to_datetime(
        economic_data["observation_date"]
    ).dt.date

    economic_data = economic_data[
        [
            "series_id",
            "observation_date",
            "value",
        ]
    ].copy()

    return economic_data