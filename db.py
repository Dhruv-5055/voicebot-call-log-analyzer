import sqlite3

def get_connection():
    conn = sqlite3.connect("calls.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def add_call(caller_id,call_timestamp,time_duration_seconds,call_type):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO calls (caller_id,call_timestamp,time_duration_seconds,call_type) VALUES (?,?,?,?)", (caller_id,call_timestamp,time_duration_seconds,call_type))
        conn.commit()
    finally:
        conn.close()