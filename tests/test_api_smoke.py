import requests


API_BASE_URL = "http://127.0.0.1:8000"


def test_health_endpoint():
    response = requests.get(
        f"{API_BASE_URL}/health",
        timeout=30,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["feature_rows"] > 0
    assert data["model"] is not None


def test_forecast_endpoint():
    payload = {
        "item_id": "FOODS_1_001",
        "store_id": "CA_1",
        "forecast_date": "2016-05-22",
    }

    response = requests.post(
        f"{API_BASE_URL}/forecast",
        json=payload,
        timeout=30,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["item_id"] == "FOODS_1_001"
    assert data["store_id"] == "CA_1"
    assert data["date"] == "2016-05-22"

    assert data["predicted_units"] >= 0
    assert data["current_price"] > 0


def test_pricing_endpoint():
    payload = {
        "item_id": "FOODS_1_001",
        "store_id": "CA_1",
        "forecast_date": "2016-05-22",
    }

    response = requests.post(
        f"{API_BASE_URL}/recommend-price",
        json=payload,
        timeout=30,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["current_price"] > 0
    assert data["recommended_price"] > 0
    assert data["expected_demand"] >= 0

    assert data["pricing_action"] in {
        "Increase",
        "Decrease",
        "Keep",
    }

    assert isinstance(
        data["recommendation_actionable"],
        bool,
    )


def test_missing_future_feature_row():
    payload = {
        "item_id": "FOODS_1_001",
        "store_id": "CA_1",
        "forecast_date": "2016-05-23",
    }

    response = requests.post(
        f"{API_BASE_URL}/forecast",
        json=payload,
        timeout=30,
    )

    assert response.status_code == 404
