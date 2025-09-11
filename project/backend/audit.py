import datetime

def log_access(user_id: str, action: str, resource: str):
    with open("audit.log", "a") as f:
        f.write(f"{datetime.datetime.now()} | {user_id} | {action} | {resource}\n")
