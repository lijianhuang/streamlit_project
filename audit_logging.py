# audit_logging.py

import pandas as pd
from filelock import FileLock
from datetime import datetime
import os

def log_event(username, customer_id, file_path):
    """
    Appends an audit log entry: timestamp, username, customer_id
    to the given file_path. Lock file is auto-generated.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lock_path = file_path + ".lock"
    new_row = pd.DataFrame([{
        "timestamp": now,
        "username": username,
        "customer_id": customer_id
    }])
    with FileLock(lock_path):
        if os.path.exists(file_path):
            new_row.to_csv(file_path, mode='a', header=False, index=False)
        else:
            new_row.to_csv(file_path, mode='w', header=True, index=False)
