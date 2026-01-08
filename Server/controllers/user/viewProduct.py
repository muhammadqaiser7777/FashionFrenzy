from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_user_token

def view_top_products():
    """View top 3 products from each category."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        categories = ['Men Clothing', 'Women Clothing', 'Men Wallet', 'Women Purse', 'Men Shoes', 'Women Shoes']
        result = {}
        for cat in categories:
            products_response = supabase.table("products").select("*").eq("category", cat).eq("status", "approved").order("created_at", desc=True).limit(3).execute()
            products = products_response.data
            for product in products:
                images_response = supabase.table("product_images").select("*").eq("product_id", product["id"]).execute()
                product["images"] = images_response.data
            result[cat] = products

        return jsonify({"products": result}), 200

    except Exception as e:
        print(f"View top products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def get_product_by_id():
    """Get a product by its unique id."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        product_id = data.get("product_id")
        if not auth_token or not product_id:
            return jsonify({"error": "auth_token and product_id are required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        product_response = supabase.table("products").select("*").eq("id", product_id).eq("status", "approved").execute()
        if not product_response.data:
            return jsonify({"error": "Product not found"}), 404

        product = product_response.data[0]
        images_response = supabase.table("product_images").select("*").eq("product_id", product_id).execute()
        product["images"] = images_response.data

        return jsonify({"product": product}), 200

    except Exception as e:
        print(f"Get product by id error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def search_products():
    """Search for products by category or title."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        query = data.get("query")
        if not auth_token or not query:
            return jsonify({"error": "auth_token and query are required"}), 400

        user_email = verify_user_token(auth_token)
        if not user_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Search in category and title
        products_response = supabase.table("products").select("*").eq("status", "approved").or_(f"category.ilike.%{query}%,title.ilike.%{query}%").execute()
        products = products_response.data
        for product in products:
            images_response = supabase.table("product_images").select("*").eq("product_id", product["id"]).execute()
            product["images"] = images_response.data

        return jsonify({"products": products}), 200

    except Exception as e:
        print(f"Search products error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500