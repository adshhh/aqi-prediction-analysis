from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

model = joblib.load('aqi_model.joblib')
scaler = joblib.load('scaler.joblib')

df = pd.read_csv('city_day.csv')

model_features = ['PM2.5', 'PM10', 'SO2', 'CO', 'NO2', 'O3']
score_RMSE = 32.19
score_MAE = 19.98
score_R_square = 0.903

class pollutants(BaseModel):
    pm2_5: float
    pm10: float
    so2: float
    co: float
    no2: float
    o3: float

@app.get("/cities")
async def cities():
    return {"cities": sorted(df['City'].unique())}

@app.post("/predict")
async def predict(data: pollutants):
    df = pd.DataFrame([[data.pm2_5, data.pm10, data.so2, data.co, data.no2, data.o3]], columns=model_features)
    pred_val = scaler.transform(df)
    pred_aqi = model.predict(pred_val)
    result = round(pred_aqi[0], 3)
    return {"predicted_aqi": float(result),
            "category": get_aqi_category(result)}

def get_aqi_category(result_aqi: float) -> str:

    if (result_aqi <= 50):
        aqi_type = "Good"
    elif (result_aqi <= 100):
        aqi_type = "Satisfactory"
    elif (result_aqi <= 200):
        aqi_type = "Moderate"
    elif (result_aqi <= 300):
        aqi_type = "Poor"
    elif (result_aqi <= 400):
        aqi_type = "Very Poor"
    else:
        aqi_type = "Severe"
    
    return aqi_type

@app.get("/history/{city_name}")
async def city_aqi_history(city_name: str):
    if (city_name not in sorted(df['City'].unique())):
        raise HTTPException(status_code=404, detail="City not found")
    city_data = df.loc[df["City"] == city_name]
    aqi_history = city_data[['Date', 'AQI', 'AQI_Bucket']]
    aqi_history = aqi_history.dropna(subset=['AQI'])
    result = aqi_history.to_dict("records")
    
    return {"aqi_history": result}

@app.get("/model_info")
async def model_info():
    feature_percentage = [round(feature_num*100, 3) for feature_num in model.feature_importances_]
    result_dict = dict(zip(model_features, feature_percentage))
    return {"RMSE_score": score_RMSE,
            "MAE_score": score_MAE,
            "R²_score": score_R_square,
            "Imp_of_features": result_dict}