import streamlit as st
import pandas as pd
import requests


BASE_URL = "http://localhost:8000"

st.title("AQI Predictor")

dict_city = requests.get(BASE_URL+"/cities").json()
list_city = dict_city["cities"]

chosen_city = st.selectbox("Pick City:", list_city, index=None, placeholder="Choose City")

val_pm2_5 = st.number_input("Enter PM2.5 Value:")
val_pm10 = st.number_input("Enter PM10 Value:")
val_so2 = st.number_input("Enter SO\u2082 Value:")
val_co = st.number_input("Enter CO Value:")
val_no2 = st.number_input("Enter NO\u2082 Value:")
val_o3 = st.number_input("Enter O\u2083 Value:")


if st.button("Predict"):
    payload = dict()
    payload["pm2_5"] = val_pm2_5
    payload["pm10"] = val_pm10
    payload["so2"] = val_so2
    payload["co"] = val_co
    payload["no2"] = val_no2
    payload["o3"] = val_o3

    response = requests.post(BASE_URL+"/predict", json=payload)
    st.write(response.json())

if chosen_city:
    city_history_dict = requests.get(BASE_URL+"/history/"+chosen_city).json()
    city_history = city_history_dict["aqi_history"]
    city_history_df = pd.DataFrame(data=city_history)
    city_history_df["Date"] = pd.to_datetime(city_history_df["Date"])
    city_history_df = city_history_df.set_index('Date')

    st.line_chart(city_history_df["AQI"])

model_stats_dict = requests.get(BASE_URL+"/model_info").json()
val_RMSE = model_stats_dict["RMSE_score"]
val_MAE = model_stats_dict["MAE_score"]
val_R_square = model_stats_dict["R²_score"]
dict_imp_feat = model_stats_dict["Imp_of_features"]

st.metric(label="RMSE:", value=val_RMSE)
st.metric(label="MAE:", value=val_MAE)
st.metric(label="R²:", value=val_R_square)

st.bar_chart(pd.Series(dict_imp_feat), y_label="Importance of each Pollutant (%)", x_label="Pollutants")
