import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from audit_logging import log_event
from auth_helper import update_password_safe
from data_manager import load_master_data
from datetime import datetime
CALL_AUDIT_PATH = "data/access_log_for_master.csv"
CONFIG_PATH = "config.yaml"

# --- Authentication Setup ---
with open(CONFIG_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

name, auth_status, username = authenticator.login('Login')

# --- Gate control: Only run sidebar and main app if authenticated ---
if auth_status is False:
    st.error("❌ Incorrect username or password.")
    st.stop()
elif auth_status is None:
    st.info("👤 Please log in to continue.")
    st.stop()

role = config["credentials"]["usernames"][username].get("role", "user")
st.session_state["role"] = role

# --- Password Reset on First Login (not admin) ---
temp_users = config.get("metadata", {}).get("temporary_passwords", [])

if role != "admin" and username in temp_users:
    if st.session_state.get("password_updated", False):
        st.success("✅ Password updated. Please log in again.")
        if st.button("Login again now"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()
    else:
        st.warning("🔐 You are using a temporary password. Please change it now.")
        with st.form(key="reset_pw_form"):
            new_pw = st.text_input("New password", type="password")
            confirm_pw = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("🔄 Update Password")
            if submitted:
                if new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password too short.")
                else:
                    success = update_password_safe(CONFIG_PATH, config, username, new_pw)
                    if success:
                        st.session_state["password_updated"] = True
                        st.rerun()
                    else:
                        st.error("⚠️ Failed to update password. Try again.")
        st.stop()

# --- Only show sidebar and logout if authenticated ---
if auth_status:
    try:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"✅ Logged in as: {name} ({username})")
    except KeyError:
        st.warning("Session expired. Please log in again.")
        if st.button("Refresh Page"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --- Load master data (all users can see all rows) ---
master_df = load_master_data()
master_df["customer_id"] = master_df["customer_id"].astype(str)

st.title("🔎 Customer ID Search")

search_id = st.text_input("Enter exact Customer ID:")

if st.button("Search"):
    if search_id:
        match = master_df[master_df["customer_id"] == search_id]
        if not match.empty:
            st.success(f"Customer {search_id} found!")
            st.write(match)
            # --- Log the access for Audit! ---
            log_event(username, search_id, CALL_AUDIT_PATH)

        else:
            st.warning("Customer ID not found.")
