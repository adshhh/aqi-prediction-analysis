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

- **Cleaning**: per-city median imputation for missing pollutant values, fit on the training
  split only and applied to test. Extreme values are kept as-is, not clipped — high-pollution
  days are real events and exactly the cases the model most needs to get right (see
  [Corrections](#corrections) for why this changed).
- **Models compared**: Multiple Linear Regression (OLS), Elastic Net, and Random Forest, each
  evaluated on an 80/20 train/test split against the raw, unmodified test set.
- **Winner**: Random Forest, by a wide margin.

| Model | RMSE | MAE | R² |
|---|---|---|---|
| Baseline (always predict mean AQI) | 135.33 | — | — |
| OLS | 59.40 | 30.99 | 0.807 |
| Elastic Net | 58.31 | 31.63 | 0.814 |
| Random Forest | 42.08 | 22.02 | 0.903 |

The deployed model is a size-constrained version of that Random Forest (`max_depth=14`,
compressed via `joblib`) to fit free-tier hosting limits — this brought the artifact down to
~6.5MB with no accuracy cost (RMSE 42.00, MAE 22.00, R² 0.904, versus the uncapped model's
42.08 / 22.02 / 0.903 above).

### How accurate is it, in plain terms?

On data the model never saw during training, its predictions are typically **within ~22 AQI
points of the true value**, and it accounts for **about 90% of the variation** in AQI across
cities. What the three metrics actually mean:

- **MAE (Mean Absolute Error) ≈ 22** — the average gap between a prediction and reality, in
  AQI points. India's AQI categories are roughly 50-100 points wide, so an error of ~22 usually
  keeps a prediction in the correct category, though it can spill into a neighboring one near a
  boundary (e.g. predicting 95 when the true value is 105).
- **RMSE (Root Mean Squared Error) ≈ 42** — similar to MAE, but squares errors before
  averaging, which penalizes large misses more heavily. RMSE being nearly double the MAE
  means the model is usually close but sometimes far off — mostly on extreme-pollution days
  (AQI above 400, and occasionally above 1,000), which are rare and hardest to predict precisely.
- **R² (R-squared) ≈ 0.90** — the share of AQI's day-to-day variation the six pollutant inputs
  explain, on a scale from 0 (no better than always guessing the average AQI) to 1 (perfect
  prediction). 0.90 means the model captures most, but not all, of what drives AQI.

By feature importance, **PM2.5 leads at ~51%, with CO close behind at ~41%**; the other four
pollutants contribute under 4% each. CO's weight is likely inflated by data quality rather
than real influence — in Ahmedabad, the CO value is identical to the NO value on ~94% of days
(a likely data-entry issue that appears in no other city), and Ahmedabad also has the highest
median AQI in the dataset, so CO partly acts as a proxy for "this is Ahmedabad". PM10's low importance
(~4%) partly reflects that it's missing entirely or almost entirely for several cities
(Lucknow, Patna, Chennai, Ahmedabad), where imputation leaves it as a near-constant.

## Is a model even necessary here?

Worth being upfront about: India's AQI has a defined, deterministic calculation (CPCB's
sub-index/breakpoint methodology) — if you have clean, complete hourly pollutant readings, you
can compute the exact correct AQI with a formula, no model required. (Applying that formula to
this dataset's *daily averages* only approximates the reported AQI, since the official
calculation uses rolling 24-hour averages and 8-hour maxima for CO and O3.) This project exists primarily
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

## Corrections

This project has been through two methodology fixes, both found by re-examining the pipeline
after the fact:

1. **Train/test leakage.** The original pipeline imputed missing values and clipped outliers on
   the full dataset *before* splitting, leaking test-set statistics into training. Fixed by
   splitting first and fitting imputation on the training split only.
2. **Clipped target.** The IQR outlier-clipping step ran over every numeric column — including
   the `AQI` target itself — capping training AQI at ~398. The model could therefore never
   predict above ~400, so the "Severe" category was unreachable. The test set was also clipped
   (using its own quartiles), which made the reported metrics look better than reality. On the
   raw test set, that model actually scored RMSE 76.0 / R² 0.68, and caught none of the 271
   test days with true AQI above 400. Fixed by removing clipping entirely; the retrained model
   scores RMSE 42.0 / R² 0.90 on the same raw test set and correctly flags 264 of those 271
   Severe days.

## Known limitations & future work

- Errors are largest on extreme-pollution days. The model now reaches the Severe range, but
  its predictions there are much less precise than in the typical 0-200 range.
- Evaluation uses a random 80/20 split rather than a time-based one, and the model's
  performance on cities it has never seen hasn't been measured — it likely relies partly on
  city-specific patterns.
- No cross-validation or systematic hyperparameter tuning — a single 80/20 split and
  largely default hyperparameters were used, given project time constraints.
- Only 6 of the dataset's 13 available pollutants are used as features.
- Models don't incorporate temperature, humidity, wind, season, or lag effects from prior
  days' AQI — likely relevant given how much day-to-day AQI can swing.
- `/predict` currently requires all six pollutant values; supporting partial input (with a
  train-derived fallback for missing values) is planned but not yet built.

## Acknowledgments

Built with AI-assisted pair programming using [Claude Code](https://claude.com/claude-code)
throughout the backend, frontend, and deployment phase — used for iterative code review,
debugging (catching issues like DataFrame construction bugs, JSON serialization edge cases,
and pandas index-alignment pitfalls), and handling mechanical setup (environment configuration,
git/GitHub, Render and Streamlit Cloud deployment). The application logic — the FastAPI
endpoints, the Streamlit UI, and the fixes for the original notebook's train/test leakage bug
and target-clipping bug — was written by me, with that review and guidance. Claude's review
identified the target-clipping bug and drafted the updated version of this README.
