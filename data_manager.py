import pandas as pd
import os
from datetime import datetime
from filelock import FileLock
import streamlit as st

MASTER_PATH = "data/large_master.csv"
CALL_LOG_PATH = "data/call_log.csv"
CALL_LOG_LOCK = "data/call_log.csv.lock"

@st.cache_data(ttl=86400)
def load_master_data():
    return pd.read_csv(MASTER_PATH, dtype={"customer_id": str})

def load_call_log():
    if os.path.exists(CALL_LOG_PATH):
        return pd.read_csv(CALL_LOG_PATH)
    return pd.DataFrame(columns=["customer_id", "called_date", "comments"])

def filter_user_data(master_df, username, role):
    if role == "admin":
        return master_df.copy()
    return master_df[master_df["assigned_user"] == username].copy()

def save_call_actions(updates):
    today = datetime.today().strftime("%d/%m/%Y")
    new_rows = [
        {
            "customer_id": row["customer_id"],
            "called_date": today,
            "comments": row.get("comments", "")
        }
        for row in updates if row["called"]
    ]
    if not new_rows:
        return
    new_df = pd.DataFrame(new_rows)
    with FileLock(CALL_LOG_LOCK):
        if os.path.exists(CALL_LOG_PATH):
            full_df = pd.read_csv(CALL_LOG_PATH)
            updated = pd.concat([full_df, new_df], ignore_index=True)
        else:
            updated = new_df
        updated.to_csv(CALL_LOG_PATH, index=False)

def get_call_history(customer_id):
    call_log_df = load_call_log()
    return call_log_df[call_log_df["customer_id"] == customer_id].sort_values("called_date")
