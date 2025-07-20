import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from auth_helper import update_password_safe
from audit_logging import log_event
from datetime import datetime
from data_manager import (
    load_master_data, filter_user_data, save_call_actions, get_call_history
)

CONFIG_PATH = "config.yaml"
CALL_AUDIT_PATH = "data/access_log_for_personal.csv"
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

# Only run this if authenticated:
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
            try:
                st.rerun()
            except Exception:
                st.info("Please refresh the page to log in again.")
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
        # Handle missing cookie gracefully
        st.warning("Session expired. Please log in again.")
        if st.button("Refresh Page"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
# --- Load and filter data (customer_id always string) ---
master_df = load_master_data()
master_df["customer_id"] = master_df["customer_id"].astype(str)
user_df = filter_user_data(master_df, username, role)

st.title("📞 Customer Call Book")

if user_df.empty:
    st.info("No leads assigned to you.")
    st.stop()

# --- Set customer_id as index for fast lookup ---
user_df["customer_id"] = user_df["customer_id"].astype(str)
user_df = user_df.set_index("customer_id")

options = user_df.index.astype(str)  # Only customer IDs
selected = st.selectbox("Select a customer:", options)

if selected: # Choosing their list
    selected_row = user_df.loc[selected]
    
    # log accss for audit
    log_event(username, selected, CALL_AUDIT_PATH)

    #show data here
    st.write(selected_row)
    # Show call history for this customer
    call_history = get_call_history(selected)
    if not call_history.empty:
        st.markdown("#### 📜 Call History")
        st.dataframe(call_history.astype(str), use_container_width=True)

    with st.form(key=f"call_form_{selected}"):
        called = st.checkbox("✅ Mark as called", value=False)
        comment = st.text_input("💬 Comment", value="")
        submitted = st.form_submit_button("💾 Save Call Action")
        if submitted:
            if not called:
                st.warning("Please tick 'Mark as called' to submit a comment.")
            else:
                updates = [{
                    "customer_id": selected,
                    "called": called,
                    "comments": comment
                }]
                save_call_actions(updates)
                st.success("✅ Call action saved.")
                try:
                    st.rerun()
                except Exception:
                    st.info("Please refresh the page to see the update.")
