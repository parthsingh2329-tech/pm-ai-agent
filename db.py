import sqlite3

DB_PATH = "pm_agent.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name, e.g. row["title"]
    return conn

def init_db():
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()