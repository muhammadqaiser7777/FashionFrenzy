from datetime import datetime
from flask import request, jsonify # type: ignore
from config.supabaseConfig import supabase
from config.mailConfig import generate_otp
from middleware.encrypt import hash_password, hash_otp, check_otp, check_password
from middleware.authToken import generate_auth_token
from password_validator import validate_password, passwordNotValidError # type: ignore
import os
import random


# Load environment variable
BACKEND_URL = os.getenv("Backend_URL")


BACKEND_URL = os.getenv("Backend_URL")


def adminLogin():
    """Handles admin login with improved error handling."""
    try:
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Ensure required fields are present
        required_fields = {"username", "password"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "Missing required fields: username and password"}), 400

        username = data.get("username")
        password = data.get("password")

        # Validate password format
        try:
            validate_password(password)
        except passwordNotValidError:
            return jsonify({"error": "Invalid password format"}), 400

        try:
            admin_response = supabase.table("admin").select("*").eq("password", password).execute()
        except Exception:
            return jsonify({"error": "Database error while fetching admin"}), 500

        if not admin_response.data:
            return jsonify({"error": "Admin not found"}), 400

        admin = admin_response.data[0]

        # Check password using check_password from auth.py
        if not check_password(password, admin["password"]):
            return jsonify({"error": "Invalid credentials"}), 400

        auth_token = admin.get("auth_token")
        if auth_token is None:
            print(f"Generating new auth_token for {password}")
            auth_token = generate_auth_token(password)

            try:
                supabase.table("admin").update({"auth_token": auth_token}).eq("password", password).execute()
            except Exception:
                return jsonify({"error": "Database error while updating auth token"}), 500


        response_data = {
            "password": admin["password"],
            "username": admin["username"],
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



def adminLogout():
    """Handles admin logout with improved error handling."""
    try:
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Ensure required fields are present
        required_fields = {"password", "auth_token"}
        if not required_fields.issubset(data.keys()):
            return jsonify({"error": "Missing required fields: password and auth_token"}), 400

        password = data.get("password")
        auth_token = data.get("auth_token")

        # Validate password format
        try:
            validate_password(password)
        except passwordNotValidError:
            return jsonify({"error": "Invalid password format"}), 400

        try:
            admin_response = supabase.table("admin").select("*").eq("password", password).execute()
        except Exception:
            return jsonify({"error": "Database error while fetching admin"}), 500

        if not admin_response.data:
            return jsonify({"error": "Admin not found"}), 400

        admin = admin_response.data[0]

        # Check if the auth_token matches the stored token
        if auth_token != admin.get("auth_token"):
            return jsonify({"error": "Invalid auth token"}), 400

        try:
            supabase.table("admin").update({"auth_token": None}).eq("password", password).execute()
        except Exception:
            return jsonify({"error": "Database error while updating auth token"}), 500

        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500