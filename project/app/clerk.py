import os
import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

def get_current_user(authorization: str = Header(...)):
    """
    Validate the user via Clerk.
    Expects 'Authorization: Bearer <token>'
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    response = requests.get(
        "https://api.clerk.dev/v1/me",
        headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_data = response.json()

    email = user_data.get("email_addresses", [{}])[0].get("email_address")
    verified = user_data.get("email_addresses", [{}])[0].get("verification", {}).get("status") == "verified"

    if not verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    role = user_data.get("public_metadata", {}).get("role", "student")

    return {"user_id": user_data["id"], "email": email, "role": role}
