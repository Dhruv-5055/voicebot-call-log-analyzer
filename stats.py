import pandas as pd
import db


def call_summary():
    conn = db.get_connection()
    try:
        rows = conn.execute("SELECT outcome, COUNT(*) FROM calls GROUP BY outcome").fetchall()
    finally:
        conn.close()

    counts = dict(rows)
    dropped = counts.get("dropped", 0)
    escalated = counts.get("escalated", 0)
    resolved = counts.get("resolved", 0)
    total = sum(counts.values())
    tagged = dropped + escalated + resolved

    if tagged == 0:
        failure_rate = 0.0
    else:
        failure_rate = (dropped + escalated) / tagged

    return {
        "total": total,
        "dropped": dropped,
        "escalated": escalated,
        "resolved": resolved,
        "failure_rate": failure_rate,
    }


def calls_per_day():
    conn = db.get_connection()
    try:
        return pd.read_sql_query(
            "SELECT substr(call_timestamp, 1, 10) AS day, COUNT(*) AS calls "
            "FROM calls GROUP BY day ORDER BY day",
            conn,
        )
    finally:
        conn.close()


def calls_per_type():
    conn = db.get_connection()
    try:
        return pd.read_sql_query(
            "SELECT call_type, COUNT(*) AS calls FROM calls GROUP BY call_type ORDER BY call_type",
            conn,
        )
    finally:
        conn.close()