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


def delete_call(call_id):
    conn=get_connection()
    try:
        current=conn.execute("DELETE from calls  WHERE call_id = ?",(call_id,))
        conn.commit()
        return current.rowcount
    finally:
        conn.close()


def import_calls(file_name,df):
    conn=get_connection()
    try:
        cur=conn.execute("INSERT INTO ingest_batches (file_name,imported_at,row_count) VALUES (?,datetime('now'),0)",(file_name,))
        batch_id=cur.lastrowid
        for row in df.itertuples(index=False):
            conn.execute("INSERT INTO calls (batch_id, caller_id, call_timestamp, time_duration_seconds, call_type) VALUES (?, ?, ?, ?, ?)", (batch_id, row.caller_id, row.call_timestamp, row.time_duration_seconds, row.call_type))
        conn.execute("UPDATE ingest_batches SET row_count = ? WHERE batch_id = ?", (len(df), batch_id))
        conn.commit()
        return batch_id
    finally:
        conn.close()


def get_call(call_id):
    conn=get_connection()
    try:
        current=conn.execute("SELECT caller_id, call_timestamp, time_duration_seconds, call_type FROM calls WHERE call_id = ?",(call_id,))
        return current.fetchone()
    finally:
        conn.close()




