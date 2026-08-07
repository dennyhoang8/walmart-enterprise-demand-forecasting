from pathlib import Path

import pandas as pd
import holidays


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "external" / "us_holidays.csv"

START_YEAR = 2011
END_YEAR = 2016


def extract_holidays() -> pd.DataFrame:
    us_holidays = holidays.US(
        years=range(START_YEAR, END_YEAR + 1)
    )

    holiday_data = pd.DataFrame(
        [
            {
                "date": date,
                "holiday_name": name,
            }
            for date, name in us_holidays.items()
        ]
    )

    holiday_data["date"] = pd.to_datetime(
        holiday_data["date"]
    ).dt.date

    holiday_data = holiday_data.sort_values("date")

    return holiday_data


if __name__ == "__main__":
    holiday_data = extract_holidays()

    holiday_data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(holiday_data.head())
    print(f"Saved {len(holiday_data):,} holiday rows.")