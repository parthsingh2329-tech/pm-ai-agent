import math
from datetime import datetime
from db import get_connection
from tools import get_project_state
from session_state import get_current_project


def _duration_days(task):
    start = task.get("start_date")
    due = task.get("due_date")
    if start and due:
        try:
            d = (datetime.fromisoformat(due) - datetime.fromisoformat(start)).days
            if d >= 1:
                return d
        except ValueError:
            pass
    hours = task.get("estimated_effort_hours")
    if hours:
        return max(1, math.ceil(hours / 8))
    return 1


def _get_dependencies(project_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.task_id AS successor_id, d.depends_on_task_id AS predecessor_id,
                  d.relationship_type
           FROM dependencies d
           JOIN tasks t ON d.task_id = t.id
           WHERE t.project_id = ?""",
        (project_id,),
    ).fetchall()
    conn.close()
    return [(r["predecessor_id"], r["successor_id"], r["relationship_type"] or "FS") for r in rows]


def _topological_order(task_ids, edges):
    successors = {t: [] for t in task_ids}
    in_degree = {t: 0 for t in task_ids}
    for pred, succ, _ in edges:
        if pred in successors and succ in in_degree:
            successors[pred].append(succ)
            in_degree[succ] += 1

    queue = [t for t in task_ids if in_degree[t] == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for nxt in successors[node]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(task_ids):
        return None  # cycle detected
    return order


def calculate_critical_path():
    project_id = get_current_project()
    if project_id is None:
        return {"error": "No active project selected."}

    tasks = get_project_state()["tasks"]
    if not tasks:
        return {"tasks": {}, "critical_path": [], "project_duration_days": 0}

    task_map = {t["id"]: t for t in tasks}
    durations = {tid: _duration_days(t) for tid, t in task_map.items()}
    edges = _get_dependencies(project_id)

    order = _topological_order(list(task_map.keys()), edges)
    if order is None:
        return {"error": "Circular dependency detected — cannot compute critical path."}

    predecessors_of = {t: [] for t in task_map}
    successors_of = {t: [] for t in task_map}
    for pred, succ, rel in edges:
        if pred in task_map and succ in task_map:
            predecessors_of[succ].append((pred, rel))
            successors_of[pred].append((succ, rel))

    es, ef = {}, {}
    for tid in order:
        bounds = [0]
        for pred, rel in predecessors_of[tid]:
            if rel == "FS":
                bounds.append(ef[pred])
            elif rel == "SS":
                bounds.append(es[pred])
            elif rel == "FF":
                bounds.append(ef[pred] - durations[tid])
            elif rel == "SF":
                bounds.append(es[pred] - durations[tid])
        es[tid] = max(bounds)
        ef[tid] = es[tid] + durations[tid]

    project_duration = max(ef.values()) if ef else 0

    lf, ls = {}, {}
    for tid in reversed(order):
        if not successors_of[tid]:
            lf[tid] = project_duration
        else:
            bounds = []
            for succ, rel in successors_of[tid]:
                if rel == "FS":
                    bounds.append(ls[succ])
                elif rel == "SS":
                    bounds.append(ls[succ] + durations[tid])
                elif rel == "FF":
                    bounds.append(lf[succ])
                elif rel == "SF":
                    bounds.append(lf[succ] + durations[tid])
            lf[tid] = min(bounds) if bounds else project_duration
        ls[tid] = lf[tid] - durations[tid]

    results = {}
    for tid in task_map:
        float_days = ls[tid] - es[tid]
        results[tid] = {
            "title": task_map[tid]["title"],
            "duration_days": durations[tid],
            "early_start": es[tid],
            "early_finish": ef[tid],
            "late_start": ls[tid],
            "late_finish": lf[tid],
            "float_days": float_days,
            "critical": float_days <= 0,
        }

    critical_path = [tid for tid in order if results[tid]["critical"]]

    return {
        "tasks": results,
        "critical_path": critical_path,
        "critical_path_titles": [task_map[t]["title"] for t in critical_path],
        "project_duration_days": project_duration,
    }