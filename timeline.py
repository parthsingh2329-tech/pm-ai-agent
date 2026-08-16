import pandas as pd
import plotly.express as px
from tools import get_project_state

STATUS_COLORS = {
    "not_started": "#94a3b8",
    "in_progress": "#3b82f6",
    "blocked": "#ef4444",
    "done": "#22c55e",
}

def get_timeline_data():
    tasks = get_project_state()["tasks"]
    rows = []
    for t in tasks:
        start = t.get("start_date") or t.get("due_date")
        finish = t.get("due_date") or t.get("start_date")
        if not start or not finish:
            continue
        rows.append({"Task": t["title"], "Start": start, "Finish": finish, "Status": t["status"]})
    return pd.DataFrame(rows)

def build_gantt_figure(df):
    if df.empty:
        return None
    df = df.copy()
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    same_day = df["Start"] == df["Finish"]
    df.loc[same_day, "Finish"] = df.loc[same_day, "Finish"] + pd.Timedelta(days=1)

    fig = px.timeline(
        df, x_start="Start", x_end="Finish", y="Task", color="Status",
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return fig