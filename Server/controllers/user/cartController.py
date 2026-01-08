from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_user_token

def add_to_cart():
    """Add a product to the user's cart."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)
        if not auth_token or not product_id:
            return jsonify({"error": "auth_token and product_id are required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check product exists and approved
        product_response = supabase.table("products").select("id, title, price, stock").eq("id", product_id).eq("status", "approved").execute()
        if not product_response.data:
            return jsonify({"error": "Product not found or not available"}), 404

        product = product_response.data[0]
        if quantity > product["stock"]:
            return jsonify({"error": "Insufficient stock"}), 400

        # Get or create cart
        cart_response = supabase.table("carts").select("id").eq("user_email", user_email).execute()
        if cart_response.data:
            cart_id = cart_response.data[0]["id"]
        else:
            cart_data = {"user_email": user_email}
            cart_insert = supabase.table("carts").insert(cart_data).execute()
            cart_id = cart_insert.data[0]["id"]

        # Check if item already in cart
        item_response = supabase.table("cart_items").select("id, quantity").eq("cart_id", cart_id).eq("product_id", product_id).execute()
        if item_response.data:
            # Update quantity
            new_quantity = item_response.data[0]["quantity"] + quantity
            if new_quantity > product["stock"]:
                return jsonify({"error": "Insufficient stock"}), 400
            supabase.table("cart_items").update({"quantity": new_quantity}).eq("id", item_response.data[0]["id"]).execute()
        else:
            # Get primary image
            image_response = supabase.table("product_images").select("image_url").eq("product_id", product_id).eq("is_primary", True).execute()
            image_url = image_response.data[0]["image_url"] if image_response.data else ""
            item_data = {
                "cart_id": cart_id,
                "product_id": product_id,
                "product_title": product["title"],
                "product_image": image_url,
                "price": product["price"],
                "quantity": quantity
            }
            supabase.table("cart_items").insert(item_data).execute()

        return jsonify({"message": "Added to cart"}), 200

    except Exception as e:
        print(f"Add to cart error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def remove_from_cart():
    """Remove a product from the user's cart."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        if not auth_token or not product_id:
            return jsonify({"error": "auth_token and product_id are required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get cart
        cart_response = supabase.table("carts").select("id").eq("user_email", user_email).execute()
        if not cart_response.data:
            return jsonify({"error": "Cart not found"}), 404

        cart_id = cart_response.data[0]["id"]

        # Delete item
        supabase.table("cart_items").delete().eq("cart_id", cart_id).eq("product_id", product_id).execute()

        return jsonify({"message": "Removed from cart"}), 200

    except Exception as e:
        print(f"Remove from cart error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def view_cart():
    """View the user's cart items."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        cart_response = supabase.table("carts").select("id").eq("user_email", user_email).execute()
        if not cart_response.data:
            return jsonify({"cart_items": []}), 200

        cart_id = cart_response.data[0]["id"]
        items_response = supabase.table("cart_items").select("*").eq("cart_id", cart_id).execute()

        return jsonify({"cart_items": items_response.data}), 200

    except Exception as e:
        print(f"View cart error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500