#!/usr/bin/env python3
"""
Test script for admin product approval endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_view_pending_products(auth_token):
    """Test the admin view-pending-products endpoint"""
    print("\nTesting /admin/view-pending-products endpoint...")
    
    url = f"{BASE_URL}/admin/view-pending-products"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }
    
    data = {
        "auth_token": auth_token
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] View pending products successful!")
            return response.json()
        else:
            print("[ERROR] View pending products failed!")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def test_edit_product_status(auth_token, product_id, status):
    """Test the admin edit-product-status endpoint"""
    print(f"\nTesting /admin/edit-product-status endpoint for product {product_id}...")
    
    url = f"{BASE_URL}/admin/edit-product-status"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000"
    }
    
    data = {
        "auth_token": auth_token,
        "product_id": product_id,
        "status": status,
        "admin_comment": "Test comment"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print(f"[SUCCESS] Edit product status successful!")
            return response.json()
        else:
            print("[ERROR] Edit product status failed!")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

def test_add_product(auth_token, category="Men's Clothing", title="Test Product", price=100, stock=10):
    """Test the retailer add-product endpoint"""
    print("\nTesting /retailer/add-product endpoint...")
    
    url = f"{BASE_URL}/retailer/add-product"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:3002"
    }
    
    data = {
        "auth_token": auth_token,
        "category": category,
        "title": title,
        "description": "Test description",
        "price": price,
        "discounted_price": 80,
        "stock": stock,
        "images": []
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("[SUCCESS] Add product successful!")
            return response.json()
        else:
            print("[ERROR] Add product failed!")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

if __name__ == "__main__":
    print("Starting admin product approval endpoint tests...\n")
    
    # These would be the actual auth tokens for testing
    # For now, this is a template for testing
    print("NOTE: This script requires valid auth tokens to test.")
    print("Replace 'YOUR_RETAILER_AUTH_TOKEN' and 'YOUR_ADMIN_AUTH_TOKEN' with actual tokens.\n")
    
    # Example usage:
    # retailer_auth = "your_retailer_auth_token"
    # admin_auth = "your_admin_auth_token"
    #
    # # First, add a product as retailer
    # product_result = test_add_product(retailer_auth, "Men's Clothing", "Test Shirt", 1500, 50)
    # if product_result:
    #     product_id = product_result.get('product_id')
    #     print(f"Added product with ID: {product_id}")
    #
    # # Then, view pending products as admin
    # pending_result = test_view_pending_products(admin_auth)
    #
    # # Finally, approve the product
    # if pending_result and pending_result.get('products'):
    #     first_product = pending_result['products'][0]
    #     test_edit_product_status(admin_auth, first_product['id'], 'approved')
    
    print("\nTests completed!")
