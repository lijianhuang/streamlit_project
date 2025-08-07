Outreach Web App
This is a sample Streamlit-based web app designed to track outreach. It features:

1.Secure user login and password reset (with temporary password handling)

2.Role-based access (e.g., admin, user)

3.Customer-specific call log and comment system

4.Audit logging of data access

5.Modular data loading and saving logic via helper modules

==========================================================================

💡 Example Use Cases (philanthropy  & Beyond)
1. Philentory: Inventory Tracking for Charities
    Replace “customer” with “item”
    Log comments on item usage, restocking, or damage
    Volunteers only see items they’re responsible for
    Add item condition/status dropdowns to the form

2. Client Case Management (e.g., MSW / Healthcare / Social Work)
Track interactions with clients
Assign staff to clients (filter by username/role)
Use comments as session notes or visit summaries
Donor Relationship Management
Track contact with donors

Record meeting notes, pledges, preferences
Monitor access to donor info

4. Volunteer Management
Track calls or meetings with volunteers
Log feedback or coordination notes
Show tasks or updates specific to each volunteer

5. Internal HR / Staff Follow-Up
    Managers log 1-on-1 conversations
    Track probation reviews or performance chats
    Ensure secure access to staff records per role

==================================================================================

Getting Started
1. Clone the repository
bash
Copy
Edit
git clone https://github.com/lijianhuang/streamlit_project
cd customer-call-book
2. Install dependencies
Create a virtual environment and install required packages:

bash
Copy
Edit
pip install -r requirements.txt
Minimal dependencies:

text
Copy
Edit
streamlit
pyyaml
streamlit-authenticator
pandas
3. Project Structure
bash
Copy
Edit
.
├── app.py                      # Main Streamlit app
├── config.yaml                 # Stores user credentials and roles
├── data/
│   └── access_log_for_personal.csv  # Audit log file
├── auth_helper.py             # Helper function to update password
├── audit_logging.py           # Logs access events
├── data_manager.py            # Loads, filters, and saves user data
└── requirements.txt
Authentication
This app uses streamlit-authenticator for login and password management. Credentials are loaded from config.yaml.

Temporary Passwords
Non-admin users with temporary passwords are forced to update on first login.

Once updated, they're logged out and asked to re-authenticate.

Role-based Access
Users are assigned a role (e.g., admin, user) in config.yaml. Access to data is filtered accordingly.

📝 Features
Secure Login
python
Copy
Edit
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)
Lead Management
Users are shown only the leads assigned to them

A dropdown lets users select a customer and record a call

all Actions
Tick “Mark as called”

Enter a comment

Submit call updates to backend storage via save_call_actions

📜 Call History + Audit Trail
Historical call records are shown per customer

Each access is logged using:

python
Copy
Edit
log_event(username, selected, CALL_AUDIT_PATH)
🛠️ Configuration
config.yaml
yaml
Copy
Edit
credentials:
  usernames:
    johndoe:
      email: john@example.com
      name: John Doe
      password: hashed_password
      role: user

cookie:
  name: some_cookie_name
  key: some_cookie_key
  expiry_days: 30

metadata:
  temporary_passwords:
    - johndoe
To generate hashed passwords:

python
Copy
Edit
import streamlit_authenticator as stauth
hashed = stauth.Hasher(['yourpassword']).generate()
print(hashed)
📈 Example Usage Flow
User logs in

App checks if it's a temporary password

If yes → prompts for password change

User sees their assigned customers

Picks one, views details and logs a call

Submission saves action + logs access

📌 Notes
Admins are exempt from forced password reset

All usernames must be unique

customer_id is treated as a string key

