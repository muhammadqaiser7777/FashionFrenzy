from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_retailer_token
from datetime import datetime

def view_orders():
    """View coming orders for the retailer, latest to oldest."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get order_items where retailer_email matches, join with orders
        # Since order_items has retailer_email, and orders has user_email
        # Need to get orders that have items from this retailer
        order_items_response = supabase.table("order_items").select("order_id").eq("retailer_email", retailer_email).execute()
        order_ids = [item["order_id"] for item in order_items_response.data]

        if not order_ids:
            return jsonify({"orders": []}), 200

        # Get orders, order by created_at desc
        orders_response = supabase.table("orders").select("*").in_("id", order_ids).order("created_at", desc=True).execute()
        orders = orders_response.data

        # For each order, get order_items
        for order in orders:
            items_response = supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
            order["items"] = items_response.data

        return jsonify({"orders": orders}), 200

    except Exception as e:
        print(f"View orders error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def confirm_order():
    """Confirm an order."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        order_id = data.get("order_id")
        if not auth_token or not order_id:
            return jsonify({"error": "auth_token and order_id are required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check if order has items from this retailer
        items_response = supabase.table("order_items").select("*").eq("order_id", order_id).eq("retailer_email", retailer_email).execute()
        if not items_response.data:
            return jsonify({"error": "Order not found or not associated with your products"}), 404

        # Update order status to confirmed
        supabase.table("orders").update({"delivery_status": "confirmed"}).eq("id", order_id).execute()

        return jsonify({"message": "Order confirmed successfully"}), 200

    except Exception as e:
        print(f"Confirm order error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def reject_order():
    """Reject an order."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        order_id = data.get("order_id")
        rejection_reason = data.get("rejection_reason")
        if not auth_token or not order_id or not rejection_reason:
            return jsonify({"error": "auth_token, order_id, and rejection_reason are required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Check if order has items from this retailer
        items_response = supabase.table("order_items").select("*").eq("order_id", order_id).eq("retailer_email", retailer_email).execute()
        if not items_response.data:
            return jsonify({"error": "Order not found or not associated with your products"}), 404

        # Update order status to rejected
        supabase.table("orders").update({
            "delivery_status": "rejected",
            "rejected_by": retailer_email,
            "rejection_reason": rejection_reason
        }).eq("id", order_id).execute()

        return jsonify({"message": "Order rejected successfully"}), 200

    except Exception as e:
        print(f"Reject order error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def dashboard():
    """Get dashboard stats for the retailer."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get order_ids for this retailer
        order_items_response = supabase.table("order_items").select("order_id, subtotal").eq("retailer_email", retailer_email).execute()
        order_ids = list(set([item["order_id"] for item in order_items_response.data]))
        subtotals = {item["order_id"]: item["subtotal"] for item in order_items_response.data}

        if not order_ids:
            return jsonify({
                "total_orders": 0,
                "total_returned": 0,
                "total_revenue": 0,
                "monthly_orders": []
            }), 200

        # Get orders
        orders_response = supabase.table("orders").select("id, delivery_status, created_at, total_amount").in_("id", order_ids).execute()
        orders = orders_response.data

        total_orders = len(orders)
        total_returned = sum(1 for o in orders if o["delivery_status"] == "returned")
        delivered_revenue = sum(subtotals.get(o["id"], 0) for o in orders if o["delivery_status"] == "delivered")
        returned_revenue = sum(subtotals.get(o["id"], 0) for o in orders if o["delivery_status"] == "returned")
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
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500