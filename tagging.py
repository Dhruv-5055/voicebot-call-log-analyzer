import db

DROPPED_MAX = 10
ESCALATED_ABOVE = 200


def tag_outcome(duration_seconds):
    if duration_seconds <= DROPPED_MAX:
        return "dropped"
    elif duration_seconds > ESCALATED_ABOVE:
        return "escalated"
    else:
        return "resolved"


def tag_untagged_calls():
    conn = db.get_connection()
    try:
        rows = conn.execute("SELECT call_id, time_duration_seconds FROM calls WHERE outcome IS NULL").fetchall()
        updates = [(tag_outcome(seconds), call_id) for call_id, seconds in rows]
        conn.executemany("UPDATE calls SET outcome = ? WHERE call_id = ?", updates)
        conn.commit()
        return len(updates)
    finally:
        conn.close()