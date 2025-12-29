from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_admin_token
from datetime import datetime

def view_all_orders():
    """View all orders."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        orders_response = supabase.table("orders").select("*").order("created_at", desc=True).execute()
        orders = orders_response.data

        for order in orders:
            items_response = supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
            order["items"] = items_response.data

        return jsonify({"orders": orders}), 200

    except Exception as e:
        print(f"View all orders error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def edit_order_status():
    """Edit order status to in_process, delivered, or returned."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        order_id = data.get("order_id")
        status = data.get("status")  # 'in_process', 'delivered', 'returned'
        if not auth_token or not order_id or status not in ["in_process", "delivered", "returned"]:
            return jsonify({"error": "auth_token, order_id, and valid status (in_process/delivered/returned) are required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        supabase.table("orders").update({"delivery_status": status}).eq("id", order_id).execute()

        return jsonify({"message": f"Order status updated to {status}"}), 200

    except Exception as e:
        print(f"Edit order status error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def admin_dashboard():
    """Get dashboard stats for admin (all orders)."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        username = verify_admin_token(auth_token)
        if not username:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get all orders
        orders_response = supabase.table("orders").select("id, delivery_status, created_at, total_amount").execute()
        orders = orders_response.data

        total_orders = len(orders)
        total_returned = sum(1 for o in orders if o["delivery_status"] == "returned")
        delivered_revenue = sum(o["total_amount"] for o in orders if o["delivery_status"] == "delivered")
        returned_revenue = sum(o["total_amount"] for o in orders if o["delivery_status"] == "returned")
        total_revenue = delivered_revenue - returned_revenue

        # Monthly orders
        monthly = {}
        for order in orders:
            created_at = order["created_at"]
            if isinstance(created_at, str):
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                date = created_at
            month = date.strftime("%Y-%m")
            monthly[month] = monthly.get(month, 0) + 1

        monthly_orders = [{"month": k, "count": v} for k, v in sorted(monthly.items())]

        return jsonify({
            "total_orders": total_orders,
            "total_returned": total_returned,
            "total_revenue": total_revenue,
            "monthly_orders": monthly_orders
        }), 200

    except Exception as e:
        print(f"Admin dashboard error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500