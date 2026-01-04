#!/usr/bin/env python3
"""
Test script for retailer signup endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_signup():
    """Test the retailer signup endpoint"""
    print("Testing /retailer/signup endpoint...")
    
    url = f"{BASE_URL}/retailer/signup"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3002"
    }
    
    data = {
        "full_name": "Test User",
        "email": "test.user.123@gmail.com",
        "password": "testpassword123",
        "gender": "male"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("[SUCCESS] Signup successful!")
            return response.json()
        else:
            print("[ERROR] Signup failed!")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def test_verify(email, auth_token, otp):
    """Test the retailer verify endpoint"""
    print("\nTesting /retailer/verify endpoint...")
    
    url = f"{BASE_URL}/retailer/verify"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3002"
    }
    
    data = {
        "email": email,
        "auth_token": auth_token,
        "otp": otp
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] Verification successful!")
            return True
        else:
            print("[ERROR] Verification failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_otp_refresh(email):
    """Test the retailer otp-refresh endpoint"""
    print("\nTesting /retailer/otp-refresh endpoint...")
    
    url = f"{BASE_URL}/retailer/otp-refresh"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3002"
    }
    
    data = {
        "email": email
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] OTP refresh successful!")
            return True
        else:
            print("[ERROR] OTP refresh failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_options():
    """Test OPTIONS preflight request"""
    print("\nTesting OPTIONS preflight...")
    
    url = f"{BASE_URL}/retailer/signup"
    headers = {
        "Origin": "http://localhost:3002",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("[SUCCESS] OPTIONS request successful!")
            return True
        else:
            print("[ERROR] OPTIONS request failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting retailer endpoint tests...\n")
    
    # Test OPTIONS preflight
    test_options()
    
    # Test signup
    signup_result = test_signup()
    
    if signup_result:
        print(f"\nEmail: {signup_result.get('email')}")
        print(f"Auth Token: {signup_result.get('auth_token')}")
        print(f"Full Name: {signup_result.get('full_name')}")
        print(f"Status: {signup_result.get('status')}")
        print(f"Profile Pic: {signup_result.get('profile_pic')}")
        
        print(f"\nCheck email for OTP. The OTP is: 123456 (placeholder)")
        print("Note: In a real test, you'd need to check the actual email for the OTP")
        
        # For testing purposes, we'll use a placeholder OTP
        # In reality, you would need to check the email for the actual OTP
        
        # Test verify with placeholder OTP (this will fail but shows the flow)
        test_verify(signup_result.get('email'), signup_result.get('auth_token'), '123456')
        
        # Test OTP refresh
        test_otp_refresh(signup_result.get('email'))
    
    print("\nTests completed!")