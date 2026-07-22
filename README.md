# AQI Prediction & Analysis

Predicting city-level Air Quality Index (AQI) in India from pollutant concentrations, deployed
as a live API and interactive web app.

**Live demo:** [aqi-prediction-analysis.streamlit.app](https://aqi-prediction-analysis.streamlit.app)
**API:** [aqi-prediction-analysis-api.onrender.com](https://aqi-prediction-analysis-api.onrender.com) ([interactive docs](https://aqi-prediction-analysis-api.onrender.com/docs))

> **Note:** the backend runs on Render's free tier, which spins down after periods of
> inactivity — the first request after a while may take 30-60 seconds to wake it up.

---

## What it does

Given six pollutant readings (PM2.5, PM10, SO2, CO, NO2, O3) for an Indian city, the app
predicts the AQI and its category (Good / Satisfactory / Moderate / Poor / Very Poor / Severe,
per CPCB's official breakpoints), and lets you explore historical AQI trends and the model's
own diagnostics.

## Dataset & Approach

Trained on `city_day.csv`, daily pollutant and AQI readings for 26 Indian cities from 2015-2020.

- **Cleaning**: per-city median imputation for missing pollutant values and IQR-based outlier
  clipping, both fit on the training split only and applied to test — an earlier version of
  this pipeline leaked test-set statistics into training via imputation/clipping computed
  before the split; that bug is fixed in the current version.
- **Models compared**: Multiple Linear Regression (OLS), Elastic Net, and Random Forest, each
  evaluated on an 80/20 train/test split.
- **Winner**: Random Forest, by a wide margin.

| Model | RMSE | R² |
|---|---|---|
| OLS | 45.47 | 0.806 |
| Elastic Net | 45.49 | 0.806 |
| Random Forest | 32.15 | 0.903 |

The deployed model is a size-constrained version of that Random Forest (`max_depth=14`,
compressed via `joblib`) to fit free-tier hosting limits — this brought the artifact down to
~8.4MB with negligible accuracy cost (RMSE 32.19, R² 0.903, versus the uncapped model's 32.15 /
0.903 above).

By feature importance, **PM2.5 dominates the model's predictions at ~71%**, with CO a distant
second at ~15% — consistent with how India's AQI calculation itself weights PM2.5 heavily.

## Is a model even necessary here?

Worth being upfront about: India's AQI has a defined, deterministic calculation (CPCB's
sub-index/breakpoint methodology) — if you have clean, complete pollutant readings, you can
compute the exact correct AQI with a formula, no model required. This project exists primarily
as an end-to-end ML and deployment exercise, not as a claim that it beats the formula. The one
place a model plausibly has a real edge: real-world sensor data is often incomplete (a station
missing a PM10 sensor, a gap in reporting), and the formula can't produce an AQI without every
sub-index — a model trained on correlated pollutant patterns can still produce a reasonable
estimate from partial input. (The current deployed API requires all six pollutants; supporting
partial input is tracked as future work below.)

## Architecture

```
Streamlit frontend  --HTTP-->  FastAPI backend  -->  Random Forest model (joblib)
(Streamlit Cloud)               (Render)              + city_day.csv (history/city lookup)
```

**API endpoints:**

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /cities` | List of all cities in the dataset |
| `POST /predict` | Predict AQI + category from six pollutant values |
| `GET /history/{city}` | Historical AQI records for a city |
| `GET /model_info` | Model evaluation metrics and feature importances |

## Tech stack

Python, pandas, scikit-learn, joblib · FastAPI, Pydantic, uvicorn · Streamlit · deployed on
Render (API) and Streamlit Community Cloud (frontend).

## Running locally

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload   # http://localhost:8000

# Frontend (separate terminal)
cd frontend
pip install -r requirements.txt
# update BASE_URL in app.py to http://localhost:8000 if pointing at a local backend
streamlit run app.py
```

## Project structure

```
├── Milestone_3_Final_Project_Report.ipynb   # data cleaning, modeling, evaluation
├── city_day.csv                             # source dataset
├── backend/
│   ├── main.py                              # FastAPI app
│   ├── aqi_model.joblib / scaler.joblib      # trained model artifacts
│   └── requirements.txt
└── frontend/
    ├── app.py                               # Streamlit app
    └── requirements.txt
```

## Known limitations & future work

- No cross-validation or systematic hyperparameter tuning — a single 80/20 split and
  largely default hyperparameters were used, given project time constraints.
- Only 6 of the dataset's 13 available pollutants are used as features.
- Models don't incorporate temperature, humidity, wind, season, or lag effects from prior
  days' AQI — likely relevant given how much day-to-day AQI can swing.
- `/predict` currently requires all six pollutant values; supporting partial input (with a
  train-derived fallback for missing values) is planned but not yet built.
- Frontend is functional but not yet visually polished (layout, styling passes pending).

## Acknowledgments

Built with AI-assisted pair programming using [Claude Code](https://claude.com/claude-code)
throughout the backend, frontend, and deployment phase — used for iterative code review,
debugging (catching issues like DataFrame construction bugs, JSON serialization edge cases,
and pandas index-alignment pitfalls), and handling mechanical setup (environment configuration,
git/GitHub, Render and Streamlit Cloud deployment). The application logic — the FastAPI
endpoints, the Streamlit UI, and the fix for the original notebook's train/test leakage bug —
was written by me, with that review and guidance.
