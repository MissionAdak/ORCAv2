"""
ORCA Engineering Dashboard
----------------------------
A web dashboard (Streamlit) for engineers to see:
  1. Agent usage - every real query run through orchestrator.py, which
     agents fired, the verdict, and how long it took.
  2. Wind/wave trends - like a stock chart, with day/week/month/year
     views, built from data polled by scheduler.py every 3 minutes.

Run it with:
    streamlit run dashboard.py

This opens in your browser automatically (usually http://localhost:8501).
Leave scheduler.py running in a separate terminal so trend data keeps
accumulating while you look at the dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

import db

st.set_page_config(page_title="ORCA Dashboard", layout="wide")
st.title("ORCA Engineering Dashboard")

tab_trends, tab_usage = st.tabs(["Wind & Wave Trends", "Agent Usage"])

# ============================================================
# TAB 1: TRENDS
# ============================================================
with tab_trends:
    locations = db.get_distinct_locations()

    if not locations:
        st.info(
            "No trend data yet. Run `python scheduler.py` in a separate terminal "
            "and let it poll for a few cycles (every 3 minutes) - this dashboard "
            "will fill in as data arrives."
        )
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_location = st.selectbox("Location", locations)
        with col2:
            timeframe = st.radio("Timeframe", ["Day", "Week", "Month", "Year"], horizontal=True)

        now = datetime.now().timestamp()
        lookback_seconds = {
            "Day": 1 * 24 * 3600,
            "Week": 7 * 24 * 3600,
            "Month": 30 * 24 * 3600,
            "Year": 365 * 24 * 3600,
        }[timeframe]

        rows = db.get_readings(location=selected_location, since_ts=now - lookback_seconds)

        if not rows:
            st.warning(f"No readings yet for {selected_location} in the last {timeframe.lower()}.")
        else:
            df = pd.DataFrame(rows)
            df["time"] = pd.to_datetime(df["timestamp"], unit="s")

            # Resample for longer timeframes so charts don't get too noisy/dense
            resample_rule = {"Day": None, "Week": "1h", "Month": "6h", "Year": "1D"}[timeframe]
            if resample_rule:
                df = df.set_index("time").resample(resample_rule).mean(numeric_only=True).dropna().reset_index()

            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=df["time"], y=df["wind_speed_kmh"],
                mode="lines", name="Wind Speed (km/h)", line=dict(color="#1f77b4"),
            ))
            fig_wind.update_layout(title=f"Wind Speed - {selected_location} ({timeframe})",
                                    xaxis_title="Time", yaxis_title="km/h", height=350)
            st.plotly_chart(fig_wind, use_container_width=True)

            fig_wave = go.Figure()
            fig_wave.add_trace(go.Scatter(
                x=df["time"], y=df["wave_height_m"],
                mode="lines", name="Wave Height (m)", line=dict(color="#2ca02c"),
            ))
            fig_wave.update_layout(title=f"Wave Height - {selected_location} ({timeframe})",
                                    xaxis_title="Time", yaxis_title="meters", height=350)
            st.plotly_chart(fig_wave, use_container_width=True)

            st.caption(f"{len(rows)} raw readings in this window.")

# ============================================================
# TAB 2: AGENT USAGE
# ============================================================
with tab_usage:
    runs = db.get_agent_runs(limit=200)

    if not runs:
        st.info("No agent runs logged yet. Run `python orchestrator.py` and answer a query - it'll show up here.")
    else:
        df_runs = pd.DataFrame(runs)
        df_runs["time"] = pd.to_datetime(df_runs["timestamp"], unit="s")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total runs logged", len(df_runs))
        col2.metric("Avg. run time", f"{df_runs['duration_ms'].mean() / 1000:.1f}s")
        col3.metric("Most recent verdict", df_runs.iloc[0]["verdict"].upper())

        st.subheader("Verdict distribution")
        verdict_counts = df_runs["verdict"].value_counts()
        fig_verdict = go.Figure(data=[go.Bar(x=verdict_counts.index, y=verdict_counts.values)])
        fig_verdict.update_layout(height=300, xaxis_title="Verdict", yaxis_title="Count")
        st.plotly_chart(fig_verdict, use_container_width=True)

        st.subheader("Recent runs")
        display_df = df_runs[["time", "location", "query", "agents_run", "verdict", "duration_ms"]].copy()
        display_df["duration_ms"] = display_df["duration_ms"].round(0)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
