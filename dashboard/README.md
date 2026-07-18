# Dashboard

The Streamlit dashboard queries Athena and visualizes A/B testing results from the curated `user_experiment_facts` table.

## Run

From the project root:

```bash
make dashboard
```

Or directly:

```bash
. .venv/bin/activate
streamlit run dashboard/streamlit_app.py
```

## Dashboard Sections

- Total users
- Best variant
- Best lift
- Sample ratio check
- Variant summary
- Control comparisons
- Activation-rate bar chart
- Segment analysis by device type, traffic source, plan type, and country
- Ship / do-not-ship decision summary
