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

def generate_auth_token_retailer(username):
    """Generate a non-expiring JWT token using username."""
    payload = {"username": username}
    token = jwt.encode(payload, SECRET_KEY_RETAILER, algorithm="HS256")
    return token