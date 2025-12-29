from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_admin_token

def view_pending_products():
    """View all pending products."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        products_response = supabase.table("products").select("*").eq("status", "pending").order("created_at", desc=True).execute()
        products = products_response.data

        # Add retailer info
        for product in products:
            retailer_response = supabase.table("retailers").select("full_name, email").eq("email", product["retailer_email"]).execute()
            if retailer_response.data:
                product["retailer"] = retailer_response.data[0]

        return jsonify({"products": products}), 200

    except Exception as e:
        print(f"View pending products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def view_approved_products():
    """View all approved products."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        products_response = supabase.table("products").select("*").eq("status", "approved").order("created_at", desc=True).execute()
        products = products_response.data

        for product in products:
            retailer_response = supabase.table("retailers").select("full_name, email").eq("email", product["retailer_email"]).execute()
            if retailer_response.data:
                product["retailer"] = retailer_response.data[0]

        return jsonify({"products": products}), 200

    except Exception as e:
        print(f"View approved products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def view_rejected_products():
    """View all rejected products."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        products_response = supabase.table("products").select("*").eq("status", "rejected").order("created_at", desc=True).execute()
        products = products_response.data

        for product in products:
            retailer_response = supabase.table("retailers").select("full_name, email").eq("email", product["retailer_email"]).execute()
            if retailer_response.data:
                product["retailer"] = retailer_response.data[0]

        return jsonify({"products": products}), 200

    except Exception as e:
        print(f"View rejected products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def edit_product_status():
    """Edit product status to approved or rejected."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        status = data.get("status")  # 'approved' or 'rejected'
        admin_comment = data.get("admin_comment", "")
        if not auth_token or not product_id or status not in ["approved", "rejected"]:
            return jsonify({"error": "auth_token, product_id, and valid status (approved/rejected) are required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        update_data = {"status": status, "admin_comment": admin_comment}
        supabase.table("products").update(update_data).eq("id", product_id).execute()

        return jsonify({"message": f"Product status updated to {status}"}), 200

    except Exception as e:
        print(f"Edit product status error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500