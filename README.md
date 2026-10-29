# Insurance Category Estimator

> A FastAPI and Streamlit app for transparent, rule-based insurance risk-category estimates.

The estimate uses age band, BMI group, smoking status, and a small city-tier lookup. Income and occupation are collected for profile context but do not affect the score.

This project does not use a trained model or claim to reproduce insurer pricing. Its output is educational only, not an insurance quote or medical advice.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

Start the API in one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Start the client in another terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend.py
```

Set `INSURANCE_API_URL` if the API is hosted somewhere other than `http://127.0.0.1:8000`.

## API

- `GET /health` checks service availability.
- `POST /predict` accepts age, height, weight, income, smoking status, city, and occupation; returns a category, score, profile summary, and scoring factors.
- `GET /docs` opens the interactive API reference.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```