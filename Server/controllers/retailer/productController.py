from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_retailer_token

def add_product():
    """Add a new product for the retailer."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        category = data.get("category")
        title = data.get("title")
        description = data.get("description")
        price = data.get("price")
        discounted_price = data.get("discounted_price")
        stock = data.get("stock")
        images = data.get("images", [])  # list of dicts: [{"image_url": "", "is_primary": bool}]

        if not all([category, title, price, stock]):
            return jsonify({"error": "category, title, price, and stock are required"}), 400

        if price <= 0 or stock < 0:
            return jsonify({"error": "price must be > 0, stock >= 0"}), 400

        # Insert product
        product_data = {
            "retailer_email": retailer_email,
            "category": category,
            "title": title,
            "description": description,
            "price": price,
            "discounted_price": discounted_price,
            "stock": stock
        }
        product_response = supabase.table("products").insert(product_data).execute()
        product_id = product_response.data[0]["id"]

        # Insert images
        for img in images:
            image_url = img.get("image_url")
            is_primary = img.get("is_primary", False)
            if image_url:
                supabase.table("product_images").insert({
                    "product_id": product_id,
                    "image_url": image_url,
                    "is_primary": is_primary
                }).execute()

        return jsonify({"message": "Product added successfully", "product_id": product_id}), 201

    except Exception as e:
        print(f"Add product error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def view_products():
    """View all products for the retailer."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get products
        products_response = supabase.table("products").select("*").eq("retailer_email", retailer_email).order("created_at", desc=True).execute()
        products = products_response.data

        # For each product, get images
        for product in products:
            images_response = supabase.table("product_images").select("*").eq("product_id", product["id"]).execute()
            product["images"] = images_response.data

        return jsonify({"products": products}), 200

    except Exception as e:
        print(f"View products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def edit_product():
    """Edit an existing product."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        if not auth_token or not product_id:
            return jsonify({"error": "auth_token and product_id are required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check if product belongs to retailer
        product_response = supabase.table("products").select("*").eq("id", product_id).eq("retailer_email", retailer_email).execute()
        if not product_response.data:
            return jsonify({"error": "Product not found or not owned by you"}), 404

        # Update fields
        update_data = {}
        allowed_fields = ["category", "title", "description", "price", "discounted_price", "stock"]
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if update_data:
            supabase.table("products").update(update_data).eq("id", product_id).execute()

        # Handle images: assume full replace or add new
        # For simplicity, delete existing and insert new
        if "images" in data:
            supabase.table("product_images").delete().eq("product_id", product_id).execute()
            for img in data["images"]:
                image_url = img.get("image_url")
                is_primary = img.get("is_primary", False)
                if image_url:
                    supabase.table("product_images").insert({
                        "product_id": product_id,
                        "image_url": image_url,
                        "is_primary": is_primary
                    }).execute()

        return jsonify({"message": "Product updated successfully"}), 200

    except Exception as e:
        print(f"Edit product error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def delete_product():
    """Delete a product."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        if not auth_token or not product_id:
            return jsonify({"error": "auth_token and product_id are required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check ownership
        product_response = supabase.table("products").select("*").eq("id", product_id).eq("retailer_email", retailer_email).execute()
        if not product_response.data:
            return jsonify({"error": "Product not found or not owned by you"}), 404

        # Delete images first
        supabase.table("product_images").delete().eq("product_id", product_id).execute()
        # Delete product
        supabase.table("products").delete().eq("id", product_id).execute()

        return jsonify({"message": "Product deleted successfully"}), 200

    except Exception as e:
        print(f"Delete product error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500