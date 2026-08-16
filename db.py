import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ["DATABASE_URL"]


class PGConnection:
    """Wraps a psycopg2 connection so the rest of the app can keep using
    sqlite-style '?' placeholders and conn.execute(...).fetchall()/.fetchone()."""

    def __init__(self, raw_conn):
        self._conn = raw_conn

    def execute(self, sql, params=()):
        pg_sql = sql.replace("?", "%s")
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(pg_sql, params)
        return cur

    def executescript(self, sql):
        cur = self._conn.cursor()
        cur.execute(sql)
        cur.close()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_connection():
    raw_conn = psycopg2.connect(DATABASE_URL)
    return PGConnection(raw_conn)


def init_db():
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized.")


if __name__ == "__main__":
    init_db()