import streamlit as st
import sqlite3
import pandas as pd
import db
from datetime import datetime
import stats
from validation import is_valid_phone
import tagging

st.title("Voice Bot Call log Analyser")

st.subheader("Add a call")
with st.form("add_form"):
    caller_number = st.text_input("Caller ID")
    timestamp = st.text_input("Timestamp (YYYY-MM-DD HH:MM:SS)")
    duration = st.number_input("Duration (seconds)", min_value=0)
    call_type = st.selectbox("Call type", ["inbound", "outbound"])
    submitted = st.form_submit_button("Save")

if submitted:
    if not caller_number.strip():
        st.warning("Please fill the Caller ID.")
    elif not timestamp.strip():
        st.warning("Please fill the Timestamp.")
    elif not is_valid_phone(caller_number):
        st.warning("Caller ID must be a 10-digit mobile number, with or without +91.")
    else:
        try:
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            st.warning("Timestamp must look like 2026-10-03 12:30:00.")
        else:
            try:
                db.add_call(caller_number, timestamp, int(duration), call_type)
            except sqlite3.IntegrityError as e:
                st.error(f"Could not save: {e}")
            else:
                st.success("Call saved.")


st.subheader("Delete a call")
with st.form("delete_form"):
    call_id = st.number_input("Call ID", min_value=1, step=1)
    confirm = st.checkbox("Yes, delete it permanently")
    delete_submitted = st.form_submit_button("Delete")

if delete_submitted:
    if not confirm:
        st.warning("Tick the box to confirm.")
    else:
        removed = db.delete_call(int(call_id))
        if removed == 0:
            st.warning("No call with that ID.")
        else:
            st.success("Call deleted.")


st.subheader("Edit a call")
edit_id = st.number_input("Call ID to edit", min_value=1, step=1, key="edit_id")
row = db.get_call(int(edit_id))
if row is None:
    st.info("No call with that ID.")
else:
    types = ["inbound", "outbound"]
    with st.form("edit_form"):
        caller_new = st.text_input("Caller ID", value=row[0], key=f"caller_{int(edit_id)}")
        timestamp_new = st.text_input("Timestamp (YYYY-MM-DD HH:MM:SS)", value=row[1], key=f"ts_{int(edit_id)}")
        duration_new = st.number_input("Duration (seconds)", min_value=0, value=int(row[2]), key=f"dur_{int(edit_id)}")
        type_new = st.selectbox("Call type", types, index=types.index(row[3]), key=f"type_{int(edit_id)}")
        edit_submitted = st.form_submit_button("Save changes")

    if edit_submitted:
        if not caller_new.strip():
            st.warning("Please fill the Caller ID.")
        elif not timestamp_new.strip():
            st.warning("Please fill the Timestamp.")
        elif not is_valid_phone(caller_new):
            st.warning("Caller ID must be a 10-digit mobile number, with or without +91.")
        else:
            try:
                datetime.strptime(timestamp_new, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                st.warning("Timestamp must look like 2026-10-03 12:30:00.")
            else:
                try:
                    changed = db.update_call(caller_new, timestamp_new, int(duration_new), type_new, int(edit_id))
                except sqlite3.IntegrityError as e:
                    st.error(f"Could not save: {e}")
                else:
                    if changed == 0:
                        st.warning("No call with that ID.")
                    else:
                        tagging.tag_untagged_calls()
                        st.success("Call updated.")


st.subheader("Import calls from a CSV file")
uploaded = st.file_uploader("Choose a CSV file", type="csv")
if uploaded is not None:
    try:
        preview_df = pd.read_csv(uploaded)
    except pd.errors.EmptyDataError:
        st.error("This file is empty.")
    else:
        st.dataframe(preview_df)
        missing = {"caller_id", "call_timestamp", "time_duration_seconds", "call_type"} - set(preview_df.columns)
        if missing:
            st.error(f"Missing columns: {', '.join(sorted(missing))}")
        elif st.button("Import file"):
            try:
                db.import_calls(uploaded.name, preview_df)
            except sqlite3.IntegrityError as e:
                st.error(f"Import failed, nothing was saved: {e}")
            else:
                tagging.tag_untagged_calls()
                st.success(f"Imported {len(preview_df)} calls.")


st.subheader("All calls")
conn = sqlite3.connect("calls.db")
df = pd.read_sql_query("SELECT * FROM calls", conn)
conn.close()

if df.empty:
    st.info("No calls have been imported yet.")
else:
    st.dataframe(df)


st.subheader("Statistics")
summary = stats.call_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total calls", summary["total"])
col2.metric("Dropped", summary["dropped"])
col3.metric("Escalated", summary["escalated"])
col4.metric("Failure rate", f"{summary['failure_rate']:.1%}")

if summary["total"] == 0:
    st.info("No calls to chart yet.")
else:
    outcomes = pd.DataFrame({
        "outcome": ["dropped", "escalated", "resolved"],
        "calls": [summary["dropped"], summary["escalated"], summary["resolved"]],
    })
    st.write("Calls per outcome")
    st.bar_chart(outcomes, x="outcome", y="calls")
    st.write("Calls per day")
    st.bar_chart(stats.calls_per_day(), x="day", y="calls")
    st.write("Calls per type")
    st.bar_chart(stats.calls_per_type(), x="CALL_TYPE", y="calls")