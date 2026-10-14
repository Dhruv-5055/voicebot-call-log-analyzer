import streamlit as st
import sqlite3
import pandas as pd
import db
from datetime import datetime

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
                st.success(f"Imported {len(preview_df)} calls.")


st.subheader("All calls")
conn = sqlite3.connect("calls.db")
df = pd.read_sql_query("SELECT * FROM calls", conn)
conn.close()

if df.empty:
    st.info("No calls have been imported yet.")
else:
    st.dataframe(df)