from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_user_token

def place_order():
    """Place an order from the user's cart."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        full_name = data.get("full_name")
        phone = data.get("phone")
        address = data.get("address")
        city = data.get("city")
        postal_code = data.get("postal_code")
        if not all([auth_token, full_name, phone, address]):
            return jsonify({"error": "auth_token, full_name, phone, address are required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get cart
        cart_response = supabase.table("carts").select("id").eq("user_email", user_email).execute()
        if not cart_response.data:
            return jsonify({"error": "Cart is empty"}), 400

        cart_id = cart_response.data[0]["id"]
        items_response = supabase.table("cart_items").select("*").eq("cart_id", cart_id).execute()
        if not items_response.data:
            return jsonify({"error": "Cart is empty"}), 400

        # Calculate total and prepare order items
        total = 0
        order_items = []
        for item in items_response.data:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            # Get retailer_email and check stock
            product_response = supabase.table("products").select("retailer_email, stock").eq("id", item["product_id"]).execute()
            if not product_response.data or product_response.data[0]["stock"] < item["quantity"]:
                return jsonify({"error": f"Insufficient stock for {item['product_title']}"}), 400
            retailer_email = product_response.data[0]["retailer_email"]
            order_items.append({
                "product_id": item["product_id"],
                "retailer_email": retailer_email,
                "product_title": item["product_title"],
                "product_image": item["product_image"],
                "price": item["price"],
                "quantity": item["quantity"],
                "subtotal": subtotal
            })

        # Insert order
        order_data = {
            "user_email": user_email,
            "total_amount": total,
            "payment_method": "COD",
            "delivery_status": "pending",
            "full_name": full_name,
            "phone": phone,
            "address": address,
            "city": city,
            "postal_code": postal_code
        }
        order_insert = supabase.table("orders").insert(order_data).execute()
        order_id = order_insert.data[0]["id"]

        # Insert order_items and deduct stock
        for item in order_items:
            item["order_id"] = order_id
            supabase.table("order_items").insert(item).execute()
            # Deduct stock
            current_stock = product_response.data[0]["stock"]  # From earlier query, but since loop, need per item
            # Actually, since product_response is per item, but in loop it's overwritten, wait.
            # Fix: get stock inside loop again or store.
            # Better: after insert, update stock
            supabase.table("products").update({"stock": supabase.table("products").select("stock").eq("id", item["product_id"]).execute().data[0]["stock"] - item["quantity"]}).eq("id", item["product_id"]).execute()

        # Clear cart
        supabase.table("cart_items").delete().eq("cart_id", cart_id).execute()

        return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201

    except Exception as e:
        print(f"Place order error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def view_orders():
    """View the user's orders and their statuses."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        orders_response = supabase.table("orders").select("*").eq("user_email", user_email).order("created_at", desc=True).execute()
        orders = orders_response.data
        for order in orders:
            items_response = supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
            order["items"] = items_response.data

        return jsonify({"orders": orders}), 200

    except Exception as e:
        print(f"View orders error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500