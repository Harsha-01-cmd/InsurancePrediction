from typing import Annotated, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


Occupation = Literal[
    "retired",
    "freelancer",
    "student",
    "government_job",
    "business_owner",
    "unemployed",
    "private_job",
]

TIER_ONE_CITIES = frozenset(
    {"mumbai", "delhi", "bengaluru", "bangalore", "chennai", "kolkata", "hyderabad", "pune"}
)
TIER_TWO_CITIES = frozenset(
    {"jaipur", "chandigarh", "indore", "lucknow", "bhopal", "nagpur", "surat", "coimbatore"}
)


class EstimateRequest(BaseModel):
    age: Annotated[int, Field(gt=0, lt=120)]
    weight_kg: Annotated[float, Field(gt=0, le=500)]
    height_m: Annotated[float, Field(gt=0.3, le=2.5)]
    income_lpa: Annotated[float, Field(ge=0)]
    smoker: bool
    city: Annotated[str, Field(min_length=1, max_length=100)]
    occupation: Occupation


class EstimateResponse(BaseModel):
    estimated_category: Literal["standard", "elevated", "high_risk"]
    risk_score: int
    factors: list[str]
    profile: dict[str, str | int | float | bool]
    notice: str


def get_city_tier(city: str) -> int:
    normalized_city = city.strip().casefold()
    if normalized_city in TIER_ONE_CITIES:
        return 1
    if normalized_city in TIER_TWO_CITIES:
        return 2
    return 3


def classify_profile(data: EstimateRequest) -> EstimateResponse:
    bmi = round(data.weight_kg / data.height_m**2, 2)
    city_tier = get_city_tier(data.city)
    score = 0
    factors: list[str] = []

    if data.age < 25:
        age_group = "young"
        age_points = 0
    elif data.age < 45:
        age_group = "adult"
        age_points = 1
    elif data.age < 60:
        age_group = "middle_aged"
        age_points = 2
    else:
        age_group = "senior"
        age_points = 3
    score += age_points
    factors.append(f"Age band ({age_group}): +{age_points}")

    if bmi < 18.5:
        bmi_group, bmi_points = "underweight", 1
    elif bmi < 25:
        bmi_group, bmi_points = "healthy", 0
    elif bmi < 30:
        bmi_group, bmi_points = "overweight", 1
    else:
        bmi_group, bmi_points = "obesity", 2
    score += bmi_points
    factors.append(f"BMI group ({bmi_group}): +{bmi_points}")

    smoker_points = 3 if data.smoker else 0
    score += smoker_points
    factors.append(f"Smoking status: +{smoker_points}")

    city_points = 2 if city_tier == 1 else 1 if city_tier == 2 else 0
    score += city_points
    factors.append(f"City tier ({city_tier}): +{city_points}")

    category = "standard" if score <= 2 else "elevated" if score <= 5 else "high_risk"
    lifestyle_risk = "high" if data.smoker and bmi >= 30 else "medium" if data.smoker or bmi >= 27 else "low"

    return EstimateResponse(
        estimated_category=category,
        risk_score=score,
        factors=factors,
        profile={
            "bmi": bmi,
            "bmi_group": bmi_group,
            "age_group": age_group,
            "lifestyle_risk": lifestyle_risk,
            "city_tier": city_tier,
            "income_lpa": data.income_lpa,
            "occupation": data.occupation,
        },
        notice="Educational rule-based estimate only; not an insurer quote or medical advice.",
    )


app = FastAPI(title="Insurance Category Estimator", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=EstimateResponse)
def predict_category(data: EstimateRequest) -> EstimateResponse:
    return classify_profile(data)