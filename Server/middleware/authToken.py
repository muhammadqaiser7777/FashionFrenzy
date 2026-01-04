import jwt  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore
from datetime import datetime, timedelta

load_dotenv()  # Load environment variables

SECRET_KEY_USER = os.getenv("SECRET_KEY_USER")
TEMP_SECRET_KEY_USER = os.getenv("TEMP_SECRET_KEY_USER")

SECRET_KEY_RETAILER = os.getenv("SECRET_KEY_RETAILER")
TEMP_SECRET_KEY_RETAILER = os.getenv("TEMP_SECRET_KEY_RETAILER")

SECRET_KEY_ADMIN = os.getenv("SECRET_KEY_ADMIN")

if not SECRET_KEY_USER:
    raise ValueError("SECRET_KEY_USER is missing. Check your .env file.")

if not TEMP_SECRET_KEY_USER:
    raise ValueError("TEMP_SECRET_KEY_USER is missing. Check your .env file.")


if not SECRET_KEY_RETAILER:
    raise ValueError("SECRET_KEY_RETAILER is missing. Check your .env file.")

if not TEMP_SECRET_KEY_RETAILER:
    raise ValueError("TEMP_SECRET_KEY_RETAILER is missing. Check your .env file.")


if not SECRET_KEY_ADMIN:
    raise ValueError("SECRET_KEY_ADMIN is missing. Check your .env file.")




EXPIRY_DURATION = timedelta(minutes=3)  # Define expiry duration

def generate_auth_token_user(email):
    """Generate a non-expiring JWT token using email."""
    payload = {"email": email}
    token = jwt.encode(payload, SECRET_KEY_USER, algorithm="HS256")
    return token

def generate_temp_token_user(email):
    """Generate a JWT token with a 3-minute expiration time and return both token and expiry time."""
    expiry_time = datetime.utcnow() + EXPIRY_DURATION
    token = jwt.encode(dict(email=email, exp=expiry_time), TEMP_SECRET_KEY_USER, algorithm="HS256")
    return token, expiry_time.isoformat()

def generate_auth_token_retailer(email):
    """Generate a non-expiring JWT token using email."""
    payload = {"email": email}
    token = jwt.encode(payload, SECRET_KEY_RETAILER, algorithm="HS256")
    return token

def generate_temp_token_retailer(email):
    """Generate a JWT token with a 3-minute expiration time and return both token and expiry time."""
    expiry_time = datetime.utcnow() + EXPIRY_DURATION
    token = jwt.encode(dict(email=email, exp=expiry_time), TEMP_SECRET_KEY_RETAILER, algorithm="HS256")
    return token, expiry_time.isoformat()

def generate_auth_token_admin(username):
    """Generate a non-expiring JWT token using username."""
    payload = {"username": username}
    token = jwt.encode(payload, SECRET_KEY_ADMIN, algorithm="HS256")
    return token

def verify_retailer_token(auth_token):
    """Verify retailer auth_token and return email if valid."""
    try:
        payload = jwt.decode(auth_token, SECRET_KEY_RETAILER, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            return None
        # Optionally, check if token exists in DB, but since it's non-expiring, maybe not necessary
        # But per user request, check in table
        from config.supabaseConfig import supabase
        user_response = supabase.table("retailer").select("email").eq("auth_token", auth_token).execute()
        if user_response.data:
            return user_response.data[0]["email"]
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_admin_token(auth_token):
    """Verify admin auth_token and return username if valid."""
    # Handle development hardcoded token
    if auth_token == "hardcoded_admin_token":
        return "admin"  # Return a default admin username
    
    try:
        payload = jwt.decode(auth_token, SECRET_KEY_ADMIN, algorithms=["HS256"])
        username = payload.get("username")
        if not username:
            return None
        from config.supabaseConfig import supabase
        admin_response = supabase.table("admin").select("username").eq("auth_token", auth_token).execute()
        if admin_response.data:
            return admin_response.data[0]["username"]
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None