from memory import add_note, search_memory
from session_state import get_current_project
import uuid
from datetime import datetime, timedelta
from db import get_connection

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "due_date": {"type": "string", "description": "ISO date, e.g. 2026-08-20"},
                    "estimated_effort_hours": {"type": "number"},
                    "depends_on": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of task_ids this task depends on",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's status or logged effort.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["not_started", "in_progress", "blocked", "done"],
                    },
                    "actual_effort_hours": {"type": "number"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_downstream",
            "description": "Recalculate due dates for tasks that depend on the given task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "new_due_date": {"type": "string"},
                },
                "required": ["task_id", "new_due_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_state",
            "description": "Get all current tasks, statuses, and due dates.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search past notes and decisions for relevant context.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Save a note or decision to project memory for later retrieval.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all existing projects.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def create_task(title, description="", due_date=None, estimated_effort_hours=None, depends_on=None):
    project_id = get_current_project()
    if project_id is None:
        return {"error": "No active project selected."}
    task_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (id, project_id, title, description, due_date, status, estimated_effort_hours) VALUES (?, ?, ?, ?, ?, 'not_started', ?)",
        (task_id, project_id, title, description, due_date, estimated_effort_hours),
    )
    for dep_id in (depends_on or []):
        conn.execute(
            "INSERT INTO dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
            (task_id, dep_id),
        )
    conn.commit()
    conn.close()
    return {"task_id": task_id, "created": True}


def update_task(task_id, status=None, actual_effort_hours=None):
    conn = get_connection()
    row = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        return {"error": f"No task with id {task_id}"}
    if status:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    if actual_effort_hours is not None:
        conn.execute("UPDATE tasks SET actual_effort_hours = ? WHERE id = ?", (actual_effort_hours, task_id))
    conn.commit()
    conn.close()
    return {"task_id": task_id, "updated": True}


def reschedule_downstream(task_id, new_due_date):
    conn = get_connection()
    conn.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (new_due_date, task_id))

    new_date = datetime.fromisoformat(new_due_date)
    shifted = []

    def find_dependents(tid):
        rows = conn.execute(
            "SELECT task_id FROM dependencies WHERE depends_on_task_id = ?", (tid,)
        ).fetchall()
        return [r["task_id"] for r in rows]

    frontier = find_dependents(task_id)
    while frontier:
        next_frontier = []
        for tid in frontier:
            row = conn.execute("SELECT due_date FROM tasks WHERE id = ?", (tid,)).fetchone()
            old_date = datetime.fromisoformat(row["due_date"]) if row["due_date"] else new_date
            if old_date <= new_date:
                shifted_date = (new_date + timedelta(days=1)).isoformat()[:10]
                conn.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (shifted_date, tid))
                shifted.append(tid)
            next_frontier.extend(find_dependents(tid))
        frontier = next_frontier

    conn.commit()
    conn.close()
    return {"task_id": task_id, "new_due_date": new_due_date, "shifted_tasks": shifted}


def get_project_state():
    project_id = get_current_project()
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,)).fetchall()
    conn.close()
    return {"tasks": [dict(row) for row in rows]}

def create_project(name):
    project_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    conn.execute("INSERT INTO projects (id, name) VALUES (?, ?)", (project_id, name))
    conn.commit()
    conn.close()
    return {"project_id": project_id, "name": name, "created": True}


def list_projects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return {"projects": [dict(row) for row in rows]}


TOOL_IMPL = {
    "create_task": create_task,
    "update_task": update_task,
    "reschedule_downstream": reschedule_downstream,
    "get_project_state": get_project_state,
    "search_memory": search_memory,
    "add_note": add_note,
    "create_project": create_project,
    "list_projects": list_projects,
}