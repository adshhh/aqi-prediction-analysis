# Tasks delegated to Claude

Tracks work explicitly handed off to Claude (rather than written by the user) so it can be
disclosed accurately in the README's acknowledgments/AI-assistance section once done.

## Pending

- [ ] **Frontend layout — two-column redesign.** Right column: the six pollutant inputs +
  Predict button + prediction result. Left column: city picker + history line chart, with a
  text caption stating the first and last date actually shown for that city (e.g. "Showing
  data from {first_date} to {last_date}") so the chart's date range is stated explicitly
  rather than left implicit. Below both columns: right side = model scores (RMSE/MAE/R²),
  left side = feature-importance bar chart. Use `st.columns(2)`.

- [ ] **Frontend styling** — increase body text font size slightly; center the "AQI
  Predictor" title (currently left-aligned via default `st.title`).

- [ ] **Number input UX** — pollutant `st.number_input` fields currently show a persistent
  `0.00` value that has to be manually deleted before typing a real number. User wants it to
  behave like a true placeholder (empty box, greyed hint text, disappears the instant you
  start typing) instead. Needs verification against the actual installed Streamlit version
  (1.59.2) for whether `st.number_input` supports `value=None` + `placeholder=...` for this —
  don't assume the API shape without checking docs/behavior at implementation time.

## Done

(none yet)
