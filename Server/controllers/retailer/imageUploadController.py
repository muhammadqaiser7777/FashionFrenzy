from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_retailer_token
import os
import uuid
from werkzeug.utils import secure_filename

def upload_product_image():
    """Upload product image and return URL."""
    try:
        # Check if auth_token is provided in headers or form data
        auth_token = request.headers.get('auth_token') or request.form.get('auth_token')
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check if file is present
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed"}), 400

        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Create upload path
        upload_dir = "static/uploads/products"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Generate public URL
        public_url = f"/static/uploads/products/{unique_filename}"
        
        return jsonify({
            "image_url": public_url,
            "message": "Image uploaded successfully"
        }), 200

    except Exception as e:
        print(f"Image upload error: {str(e)}")
        return jsonify({"error": "Failed to upload image"}), 500

def delete_product_image():
    """Delete a product image file."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        image_url = data.get("image_url")
        
        if not auth_token or not image_url:
            return jsonify({"error": "auth_token and image_url are required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Extract filename from URL
        if image_url.startswith("/static/uploads/products/"):
            filename = image_url.split("/")[-1]
            file_path = os.path.join("static/uploads/products", filename)
            
            # Delete file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({"message": "Image deleted successfully"}), 200
            else:
                return jsonify({"error": "Image file not found"}), 404
        else:
            return jsonify({"error": "Invalid image URL"}), 400

    except Exception as e:
        print(f"Image delete error: {str(e)}")
        return jsonify({"error": "Failed to delete image"}), 500

def get_uploaded_images():
    """Get list of uploaded images for the retailer."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get all images from product_images table for this retailer
        # First get product IDs for this retailer
        products_response = supabase.table("products").select("id").eq("retailer_email", retailer_email).execute()
        product_ids = [p["id"] for p in products_response.data]
        
        if not product_ids:
            return jsonify({"images": []}), 200
        
        # Get images for these products
        images_response = supabase.table("product_images").select("*").in_("product_id", product_ids).execute()
        
        return jsonify({"images": images_response.data}), 200

    except Exception as e:
        print(f"Get images error: {str(e)}")
        return jsonify({"error": "Failed to retrieve images"}), 500