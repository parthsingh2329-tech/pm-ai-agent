CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'not_started',
    estimated_effort_hours REAL,
    actual_effort_hours REAL
);

CREATE TABLE IF NOT EXISTS dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id)
);