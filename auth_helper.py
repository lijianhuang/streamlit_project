import yaml
from filelock import FileLock
from streamlit_authenticator import Hasher

def update_password_safe(config_path, config, username, new_password):
    try:
        hashed = Hasher([new_password]).generate()[0]
        config["credentials"]["usernames"][username]["password"] = hashed
        if "metadata" in config and "temporary_passwords" in config["metadata"]:
            if username in config["metadata"]["temporary_passwords"]:
                config["metadata"]["temporary_passwords"].remove(username)
        lock_path = f"{config_path}.lock"
        with FileLock(lock_path):
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Password update failed: {e}")
        return False
