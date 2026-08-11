# Tasks delegated to Claude

Tracks work explicitly handed off to Claude (rather than written by the user) so it can be
disclosed accurately in the README's acknowledgments/AI-assistance section once done.

## Pending

(none yet)

## Done

- [x] **Frontend layout — two-column redesign.** Right column: the six pollutant inputs +
  Predict button + prediction result. Left column: city picker + history line chart, with a
  text caption stating the first and last date actually shown for that city (e.g. "Showing
  data from {first_date} to {last_date}") so the chart's date range is stated explicitly
  rather than left implicit. Below both columns: right side = model scores (RMSE/MAE/R²),
  left side = feature-importance bar chart. Used `st.columns(2)`, with a spacer-column trick
  (`st.columns([1, 5, 1])`) for centered side margins and `gap="large"` for visible separation
  between columns.

- [x] **Frontend styling** — increased body text font size via `.streamlit/config.toml`
  (`baseFontSize = 18`); centered the "AQI Predictor" title via `st.title(text_alignment="center")`.

- [x] **Number input UX** — pollutant `st.number_input` fields now use `value=None` +
  `placeholder="e.g. ..."`, confirmed supported in the installed Streamlit version (1.61.1):
  empty box with greyed hint text that disappears on typing, instead of a persistent `0.00`.

- [x] **Plain-language model accuracy on frontend** — added a headline sentence under the
  model-scores panel translating MAE/R² into plain terms ("predictions are typically within
  X AQI points... explains about Y% of the variation"), plus hover tooltips (`help=`) on each
  metric (MAE, RMSE, R²) explaining what it means in simple language.
