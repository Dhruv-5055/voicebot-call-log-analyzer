import streamlit as st
import sqlite3
import pandas as pd


st.title("Voice Bot Call log Analyser")

conn = sqlite3.connect("calls.db")
df = pd.read_sql_query("SELECT * FROM calls", conn)
conn.close()


if df.empty is True:
    st.info("Database found")
else:
    st.dataframe("calls.db")

   