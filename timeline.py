import pandas as pd
import plotly.express as px
from tools import get_project_state
from cpm import calculate_critical_path

STATUS_COLORS = {
    "not_started": "#94a3b8",
    "in_progress": "#3b82f6",
    "blocked": "#ef4444",
    "done": "#22c55e",
}
CRITICAL_COLOR = "#dc2626"


def get_timeline_data():
    tasks = get_project_state()["tasks"]
    cpm_result = calculate_critical_path()
    cpm_tasks = cpm_result.get("tasks", {}) if "error" not in cpm_result else {}

    rows = []
    for t in tasks:
        start = t.get("start_date") or t.get("due_date")
        finish = t.get("due_date") or t.get("start_date")
        if not start or not finish:
            continue
        cpm_info = cpm_tasks.get(t["id"], {})
        is_critical = cpm_info.get("critical", False)
        float_days = cpm_info.get("float_days")
        rows.append({
            "Task": t["title"],
            "Start": start,
            "Finish": finish,
            "Status": "Critical" if is_critical else t["status"],
            "Float (days)": float_days if float_days is not None else "n/a",
        })
    return pd.DataFrame(rows), cpm_result


def build_gantt_figure(df):
    if df.empty:
        return None
    df = df.copy()
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    same_day = df["Start"] == df["Finish"]
    df.loc[same_day, "Finish"] = df.loc[same_day, "Finish"] + pd.Timedelta(days=1)