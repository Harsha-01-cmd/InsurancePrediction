import os

import requests
import streamlit as st


API_URL = os.getenv("INSURANCE_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Insurance Estimate", page_icon="I", layout="wide")
st.title("Insurance Category Estimate")

form_column, result_column = st.columns([1, 1.15], gap="large")

with form_column:
    st.subheader("Applicant profile")
    with st.form("estimate_form"):
        age = st.number_input("Age", min_value=1, max_value=119, value=32)
        weight_kg = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=68.0)
        height_m = st.number_input("Height (m)", min_value=0.31, max_value=2.5, value=1.72)
        income_lpa = st.number_input("Annual income (LPA)", min_value=0.0, value=12.0)
        smoker = st.checkbox("Currently smokes")
        city = st.text_input("City", value="Pune")
        occupation = st.selectbox(
            "Occupation",
            [
                "private_job",
                "government_job",
                "business_owner",
                "freelancer",
                "student",
                "unemployed",
                "retired",
            ],
        )
        submitted = st.form_submit_button("Estimate category", type="primary", use_container_width=True)

with result_column:
    st.subheader("Estimate")
    if submitted:
        profile = {
            "age": age,
            "weight_kg": weight_kg,
            "height_m": height_m,
            "income_lpa": income_lpa,
            "smoker": smoker,
            "city": city,
            "occupation": occupation,
        }
        try:
            response = requests.post(f"{API_URL}/predict", json=profile, timeout=15)
            response.raise_for_status()
            result = response.json()
            st.metric("Estimated category", result["estimated_category"].replace("_", " ").title())
            score_col, bmi_col, tier_col = st.columns(3)
            score_col.metric("Risk score", result["risk_score"])
            bmi_col.metric("BMI", result["profile"]["bmi"])
            tier_col.metric("City tier", result["profile"]["city_tier"])
            st.markdown("**Scoring factors**")
            for factor in result["factors"]:
                st.write(f"- {factor}")
            st.caption(result["notice"])
        except requests.HTTPError as error:
            st.error(f"The API rejected this profile: {error.response.text}")
        except requests.RequestException:
            st.error(f"Could not reach the API at {API_URL}. Start the FastAPI server and try again.")
    else:
        st.info("Complete the profile to see an estimate.")