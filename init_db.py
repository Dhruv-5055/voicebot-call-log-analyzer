import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS ingest_batches (
batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
file_name TEXT NOT NULL UNIQUE,
imported_at TEXT NOT NULL,
row_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS calls  (
CALL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
batch_id INTEGER  REFERENCES ingest_batches(batch_id),
CALLER_ID TEXT NOT NULL,
CALLER_NAME TEXT,
RECEIVER_NAME TEXT,
CALL_TIMESTAMP TEXT NOT NULL,
TIME_DURATION_SECONDS INTEGER NOT NULL,
CALL_TYPE TEXT NOT NULL CHECK (CALL_TYPE IN ('inbound','outbound')),
LANGUAGE TEXT,
TOPIC TEXT ,
ASR_CONFIDENCE REAL,
RETRY_COUNT INTEGER NOT NULL DEFAULT 0,
OUTCOME TEXT CHECK (OUTCOME IN( 'resolved', 'escalated' ,'dropped'))

);

"""

def init_db():
    conn = sqlite3.connect("calls.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database ready: calls.db")

