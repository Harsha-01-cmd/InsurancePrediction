from fastapi.testclient import TestClient

from main import app, get_city_tier


client = TestClient(app)


def test_prediction_returns_explainable_estimate():
    response = client.post(
        "/predict",
        json={
            "age": 32,
            "weight_kg": 68,
            "height_m": 1.72,
            "income_lpa": 12,
            "smoker": False,
            "city": " Mumbai ",
            "occupation": "private_job",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["estimated_category"] == "elevated"
    assert result["risk_score"] == 3
    assert result["profile"]["city_tier"] == 1
    assert result["profile"]["bmi_group"] == "healthy"
    assert len(result["factors"]) == 4
    assert "not an insurer quote" in result["notice"]


def test_city_tier_normalizes_case_and_whitespace():
    assert get_city_tier("  PUNE ") == 1
    assert get_city_tier("Indore") == 2
    assert get_city_tier("Unknown town") == 3


def test_invalid_age_and_occupation_are_rejected():
    payload = {
        "age": 0,
        "weight_kg": 68,
        "height_m": 1.72,
        "income_lpa": 12,
        "smoker": False,
        "city": "Pune",
        "occupation": "private_job",
    }
    assert client.post("/predict", json=payload).status_code == 422

    payload["age"] = 32
    payload["occupation"] = "astronaut"
    assert client.post("/predict", json=payload).status_code == 422