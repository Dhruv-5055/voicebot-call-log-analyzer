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


def update_call(caller_id,call_timestamp,time_duration_seconds,call_type,call_id):
    conn=get_connection()
    try:
        cur = conn.execute("UPDATE calls SET caller_id = ?, call_timestamp = ?, time_duration_seconds = ?, call_type = ? WHERE call_id = ?", (caller_id,call_timestamp,time_duration_seconds,call_type,call_id))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()