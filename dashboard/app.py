"""
Streamlit Ops Dashboard — run with:
    streamlit run dashboard/app.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ops.logger import QueryLogger

st.set_page_config(
    page_title="Research Agent — Ops Dashboard",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Research Agent — Ops Dashboard")
st.caption("Real-time observability across all agent executions")

logger = QueryLogger()

# ── Refresh ──────────────────────────────────────────────────────────────────
if st.button("🔄 Refresh"):
    st.rerun()

# ── Summary metrics ──────────────────────────────────────────────────────────
stats = logger.summary_stats()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Queries",    stats.get("total_queries", 0))
c2.metric("Avg Latency (ms)", f"{stats.get('avg_latency_ms', 0):.0f}")
c3.metric("Min Latency (ms)", f"{stats.get('min_latency_ms', 0):.0f}")
c4.metric("Successful",       stats.get("successful", 0))
c5.metric("Failed",           stats.get("failed", 0))

st.divider()

# ── Load raw data ────────────────────────────────────────────────────────────
rows = logger.fetch_all()

if not rows:
    st.info("No queries logged yet. Run `python main.py` to generate some data.")
    st.stop()

df = pd.DataFrame(rows)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["tools_used"] = df["tools_used"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
df["tools_str"]  = df["tools_used"].apply(lambda x: ", ".join(x) if x else "none")

# ── Latency over time ─────────────────────────────────────────────────────────
st.subheader("⏱️ Latency Over Time")
fig_lat = px.line(
    df.sort_values("timestamp"),
    x="timestamp", y="latency_ms",
    markers=True,
    color_discrete_sequence=["#7F77DD"],
    labels={"latency_ms": "Latency (ms)", "timestamp": "Time"},
)
fig_lat.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
st.plotly_chart(fig_lat, use_container_width=True)

col1, col2 = st.columns(2)

# ── Tool usage frequency ──────────────────────────────────────────────────────
with col1:
    st.subheader("🛠️ Tool Usage Frequency")
    tool_counts: dict = {}
    for tools in df["tools_used"]:
        for t in tools:
            tool_counts[t] = tool_counts.get(t, 0) + 1
    if tool_counts:
        fig_tools = px.bar(
            x=list(tool_counts.keys()),
            y=list(tool_counts.values()),
            labels={"x": "Tool", "y": "Calls"},
            color=list(tool_counts.keys()),
            color_discrete_sequence=["#7F77DD", "#1D9E75", "#D85A30"],
        )
        fig_tools.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=260)
        st.plotly_chart(fig_tools, use_container_width=True)
    else:
        st.info("No tool usage data yet.")

# ── Success vs failure ────────────────────────────────────────────────────────
with col2:
    st.subheader("✅ Success vs Failure")
    status_counts = df["success"].value_counts().rename({1: "Success", 0: "Failed"})
    fig_pie = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color_discrete_sequence=["#1D9E75", "#D85A30"],
        hole=0.4,
    )
    fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=260)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Query log table ───────────────────────────────────────────────────────────
st.subheader("📋 Recent Queries")
display_df = df[["timestamp", "query", "tools_str", "latency_ms", "answer_len", "success"]].copy()
display_df.columns = ["Timestamp", "Query", "Tools Used", "Latency (ms)", "Answer Length", "Success"]
display_df["Success"] = display_df["Success"].map({1: "✅", 0: "❌"})
display_df["Latency (ms)"] = display_df["Latency (ms)"].round(0).astype(int)
st.dataframe(display_df, use_container_width=True, hide_index=True)
