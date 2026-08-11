import streamlit as st
import pandas as pd
import requests

BASE_URL = "https://aqi-prediction-analysis-api.onrender.com"

st.set_page_config(layout="wide")

spacer_left, center, spacer_right = st.columns([1, 5, 1])

with center:
    st.title("AQI Predictor", text_alignment="center")

    dict_city = requests.get(BASE_URL + "/cities").json()
    list_city = dict_city["cities"]

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        chosen_city = st.selectbox("Pick City:", list_city, index=None, placeholder="Choose City")

        if chosen_city:
            city_history_dict = requests.get(BASE_URL + "/history/" + chosen_city).json()
            city_history = city_history_dict["aqi_history"]
            city_history_df = pd.DataFrame(data=city_history)
            city_history_df["Date"] = pd.to_datetime(city_history_df["Date"])
            city_history_df = city_history_df.set_index("Date")

            st.line_chart(city_history_df["AQI"])
            st.caption(
                f"Showing data from {city_history_df.index.min().date()} "
                f"to {city_history_df.index.max().date()}"
            )

    with right_col:
        val_pm2_5 = st.number_input("Enter PM2.5 Value:", value=None, placeholder="e.g. 80")
        val_pm10 = st.number_input("Enter PM10 Value:", value=None, placeholder="e.g. 120")
        val_so2 = st.number_input("Enter SO₂ Value:", value=None, placeholder="e.g. 15")
        val_co = st.number_input("Enter CO Value:", value=None, placeholder="e.g. 1.2")
        val_no2 = st.number_input("Enter NO₂ Value:", value=None, placeholder="e.g. 40")
        val_o3 = st.number_input("Enter O₃ Value:", value=None, placeholder="e.g. 30")

        if st.button("Predict"):
            payload = {
                "pm2_5": val_pm2_5,
                "pm10": val_pm10,
                "so2": val_so2,
                "co": val_co,
                "no2": val_no2,
                "o3": val_o3,
            }

            if None in payload.values():
                st.warning("Please fill in all six pollutant values.")
            else:
                result = requests.post(BASE_URL + "/predict", json=payload).json()
                result_col1, result_col2 = st.columns(2)
                with result_col1:
                    st.metric(label="Predicted AQI:", value=result["predicted_aqi"])
                with result_col2:
                    st.metric(label="Category:", value=result["category"])

    model_stats_dict = requests.get(BASE_URL + "/model_info").json()
    val_RMSE = model_stats_dict["RMSE_score"]
    val_MAE = model_stats_dict["MAE_score"]
    val_R_square = model_stats_dict["R²_score"]
    dict_imp_feat = model_stats_dict["Imp_of_features"]

    bottom_left, bottom_right = st.columns(2, gap="large")

    with bottom_left:
        st.bar_chart(pd.Series(dict_imp_feat), y_label="Importance of each Pollutant (%)", x_label="Pollutants")

    with bottom_right:
        st.markdown("**Model Accuracy**")
        st.write(
            f"On data the model has never seen, predictions are typically within "
            f"**{val_MAE:.0f} AQI points** of the real value, and the model explains "
            f"about **{val_R_square * 100:.0f}%** of the variation in AQI across cities."
        )
        st.metric(
            label="Avg. Error (MAE)", value=round(val_MAE, 1),
            help="On average, how far off a prediction is from the true AQI value. Lower is better."
        )
        st.metric(
            label="Typical Error (RMSE)", value=round(val_RMSE, 1),
            help="Similar to average error, but penalizes large misses more heavily. Lower is better."
        )
        st.metric(
            label="Fit Score (R²)", value=round(val_R_square, 2),
            help="Share of AQI variation the model explains, from 0 to 1. Closer to 1 means better fit."
        )
