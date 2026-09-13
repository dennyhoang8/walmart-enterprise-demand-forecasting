"""
Streamlit dashboard for the Walmart M5 demand forecasting
and dynamic pricing project.

This app talks to the FastAPI backend.

Local development:
http://127.0.0.1:8000

Docker:
http://api:8000
"""

import os
from datetime import date

import requests
import streamlit as st


# ============================================================
# API CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Walmart Demand Forecasting & Dynamic Pricing",
    page_icon="📦",
    layout="wide",
)


# ============================================================
# HELPERS
# ============================================================

def api_get(path: str):
    """
    Send a GET request to the FastAPI backend.
    """

    response = requests.get(
        f"{API_BASE_URL}{path}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def api_post(path: str, payload: dict):
    """
    Send a POST request to the FastAPI backend.
    """

    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload,
        timeout=30,
    )

    if response.status_code >= 400:
        try:
            detail = response.json().get(
                "detail",
                response.text,
            )
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"API error {response.status_code}: {detail}"
        )

    return response.json()


def format_currency(value):
    """
    Format a numeric value as currency.
    """

    if value is None:
        return "N/A"

    return f"${value:,.2f}"


def format_percent(value):
    """
    Format a decimal percentage.
    """

    if value is None:
        return "N/A"

    return f"{value:.2%}"


# ============================================================
# HEADER
# ============================================================

st.title(
    "Walmart Demand Forecasting & Dynamic Pricing"
)

st.caption(
    "Forecast item demand and evaluate scenario-based price "
    "recommendations using the Walmart M5 forecasting pipeline."
)


# ============================================================
# API STATUS
# ============================================================

st.subheader(
    "System Status"
)

try:
    health = api_get(
        "/health"
    )

    if health.get(
        "status"
    ) == "healthy":

        st.success(
            "FastAPI backend is healthy."
        )

        status_col1, status_col2 = st.columns(
            2
        )

        with status_col1:
            st.metric(
                "Loaded Feature Rows",
                f"{health.get('feature_rows', 0):,}",
            )

        with status_col2:
            st.metric(
                "Forecast Model",
                health.get(
                    "model",
                    "Unknown",
                ),
            )

    else:
        st.warning(
            "FastAPI is running but is not fully ready."
        )

except Exception as exc:
    st.error(
        "Could not connect to the FastAPI backend."
    )

    st.write(
        f"API URL being used: {API_BASE_URL}"
    )

    st.caption(
        str(exc)
    )

    st.stop()


st.divider()


# ============================================================
# INPUTS
# ============================================================

st.subheader(
    "Forecast Inputs"
)

input_col1, input_col2, input_col3 = st.columns(
    3
)

with input_col1:
    item_id = st.text_input(
        "Item ID",
        value="FOODS_1_001",
    )

with input_col2:
    store_id = st.text_input(
        "Store ID",
        value="CA_1",
    )

with input_col3:
    forecast_date = st.date_input(
        "Forecast Date",
        value=date(
            2016,
            5,
            22,
        ),
    )


payload = {
    "item_id": item_id.strip(),
    "store_id": store_id.strip(),
    "forecast_date": forecast_date.isoformat(),
}


st.caption(
    "Current development limitation: the API can score dates already "
    "present in the processed feature dataset. True future-date "
    "recursive forecasting will be added later."
)


# ============================================================
# DEMAND FORECAST
# ============================================================

st.subheader(
    "Demand Forecast"
)

if st.button(
    "Run Demand Forecast",
    use_container_width=True,
):

    try:
        forecast_result = api_post(
            "/forecast",
            payload,
        )

        st.session_state[
            "forecast_result"
        ] = forecast_result

    except Exception as exc:
        st.error(
            str(exc)
        )


if "forecast_result" in st.session_state:

    result = st.session_state[
        "forecast_result"
    ]

    metric_col1, metric_col2, metric_col3 = st.columns(
        3
    )

    with metric_col1:
        st.metric(
            "Predicted Units",
            f"{result['predicted_units']:.3f}",
        )

    with metric_col2:
        st.metric(
            "Current Price",
            format_currency(
                result.get(
                    "current_price"
                )
            ),
        )

    with metric_col3:
        st.metric(
            "Forecast Date",
            result["date"],
        )

    st.caption(
        f"Item: {result['item_id']} | "
        f"Store: {result['store_id']}"
    )


st.divider()


# ============================================================
# DYNAMIC PRICING
# ============================================================

st.subheader(
    "Dynamic Pricing Recommendation"
)

if st.button(
    "Generate Price Recommendation",
    use_container_width=True,
):

    try:
        pricing_result = api_post(
            "/recommend-price",
            payload,
        )

        st.session_state[
            "pricing_result"
        ] = pricing_result

    except Exception as exc:
        st.error(
            str(exc)
        )


if "pricing_result" in st.session_state:

    pricing = st.session_state[
        "pricing_result"
    ]

    price_col1, price_col2, price_col3, price_col4 = st.columns(
        4
    )

    with price_col1:
        st.metric(
            "Current Price",
            format_currency(
                pricing["current_price"]
            ),
        )

    with price_col2:
        st.metric(
            "Recommended Price",
            format_currency(
                pricing["recommended_price"]
            ),
        )

    with price_col3:
        st.metric(
            "Price Change",
            format_percent(
                pricing["recommended_change_pct"]
            ),
        )

    with price_col4:
        st.metric(
            "Pricing Action",
            pricing["pricing_action"],
        )


    st.markdown(
        "### Expected Demand & Revenue"
    )

    revenue_col1, revenue_col2, revenue_col3, revenue_col4 = st.columns(
        4
    )

    with revenue_col1:
        st.metric(
            "Predicted Units",
            f"{pricing['predicted_units']:.3f}",
        )

    with revenue_col2:
        st.metric(
            "Scenario Demand",
            f"{pricing['expected_demand']:.3f}",
        )

    with revenue_col3:
        st.metric(
            "Current Expected Revenue",
            format_currency(
                pricing[
                    "current_expected_revenue"
                ]
            ),
        )

    with revenue_col4:
        st.metric(
            "Recommended Expected Revenue",
            format_currency(
                pricing[
                    "recommended_expected_revenue"
                ]
            ),
        )


    st.markdown(
        "### Recommendation Quality"
    )

    quality_col1, quality_col2, quality_col3 = st.columns(
        3
    )

    with quality_col1:
        st.metric(
            "Simulated Revenue Lift",
            format_currency(
                pricing[
                    "simulated_revenue_lift"
                ]
            ),
        )

    with quality_col2:
        st.metric(
            "Simulated Lift %",
            format_percent(
                pricing[
                    "simulated_revenue_lift_pct"
                ]
            ),
        )

    with quality_col3:
        st.metric(
            "Actionable",
            "Yes"
            if pricing[
                "recommendation_actionable"
            ]
            else "No",
        )


    st.markdown(
        "### Elasticity"
    )

    elasticity_col1, elasticity_col2, elasticity_col3 = st.columns(
        3
    )

    with elasticity_col1:
        st.metric(
            "Elasticity",
            f"{pricing['elasticity']:.3f}",
        )

    with elasticity_col2:
        st.metric(
            "Elasticity Source",
            pricing[
                "elasticity_source"
            ],
        )

    with elasticity_col3:
        st.metric(
            "Observed Price Changes",
            pricing[
                "elasticity_observations"
            ],
        )


    if pricing[
        "recommendation_actionable"
    ]:
        st.success(
            "This recommendation passes the minimum simulated "
            "revenue-lift threshold."
        )

    else:
        st.info(
            "The model does not consider this price change actionable."
        )


    with st.expander(
        "View Full API Response"
    ):
        st.json(
            pricing
        )


# ============================================================
# PROJECT NOTES
# ============================================================

st.divider()

st.subheader(
    "Project Notes"
)

st.write(
    """
    - Demand forecasts come from the trained Poisson Histogram Gradient Boosting model.
    - Price recommendations are scenario-based rather than causal estimates.
    - Price changes are constrained by the pricing guardrails developed in Notebook 06.
    - The current development workflow uses historically available model-ready rows.
    - A future production version should add strict multi-step future forecasting,
      live feature generation, stronger elasticity estimation, and controlled pricing experiments.
    """
)