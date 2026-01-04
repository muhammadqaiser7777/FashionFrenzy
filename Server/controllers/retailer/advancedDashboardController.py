from flask import request, jsonify
from config.supabaseConfig import supabase
from middleware.authToken import verify_retailer_token
from datetime import datetime, timedelta
from collections import defaultdict

def get_advanced_dashboard_stats():
    """Get comprehensive dashboard statistics for the retailer."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get all order items for this retailer
        order_items_response = supabase.table("order_items").select("*").eq("retailer_email", retailer_email).execute()
        order_items = order_items_response.data
        
        if not order_items:
            return jsonify({
                "total_orders": 0,
                "pending_orders": 0,
                "confirmed_orders": 0,
                "rejected_orders": 0,
                "delivered_orders": 0,
                "total_revenue": 0,
                "total_products": 0,
                "low_stock_products": 0,
                "monthly_revenue": [],
                "top_selling_products": [],
                "recent_orders": []
            }), 200

        # Get unique order IDs
        order_ids = list(set([item["order_id"] for item in order_items]))
        
        # Get all orders for this retailer
        orders_response = supabase.table("orders").select("*").in_("id", order_ids).execute()
        orders = orders_response.data

        # Get all products for this retailer
        products_response = supabase.table("products").select("*").eq("retailer_email", retailer_email).execute()
        products = products_response.data

        # Calculate statistics
        total_orders = len(orders)
        pending_orders = sum(1 for o in orders if o.get("delivery_status", "").lower() in ["pending", "processing", "confirmed"])
        confirmed_orders = sum(1 for o in orders if o.get("delivery_status", "").lower() == "confirmed")
        rejected_orders = sum(1 for o in orders if o.get("delivery_status", "").lower() == "rejected")
        delivered_orders = sum(1 for o in orders if o.get("delivery_status", "").lower() == "delivered")

        # Calculate revenue
        order_revenues = {}
        for item in order_items:
            order_id = item["order_id"]
            order_revenues[order_id] = order_revenues.get(order_id, 0) + item.get("subtotal", 0)

        total_revenue = sum(
            revenue for order_id, revenue in order_revenues.items()
            if next((o for o in orders if o["id"] == order_id), {}).get("delivery_status") == "delivered"
        )

        # Low stock products (less than 10 items)
        low_stock_products = sum(1 for p in products if p.get("stock", 0) < 10)

        # Monthly revenue for last 12 months
        monthly_revenue = get_monthly_revenue_data(orders, order_revenues)
        
        # Top selling products
        top_selling_products = get_top_selling_products(order_items, products)
        
        # Recent orders (last 10)
        recent_orders = get_recent_orders(orders, order_items)

        return jsonify({
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "rejected_orders": rejected_orders,
            "delivered_orders": delivered_orders,
            "total_revenue": round(total_revenue, 2),
            "total_products": len(products),
            "low_stock_products": low_stock_products,
            "monthly_revenue": monthly_revenue,
            "top_selling_products": top_selling_products,
            "recent_orders": recent_orders
        }), 200

    except Exception as e:
        print(f"Advanced dashboard error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def get_monthly_revenue_data(orders, order_revenues):
    """Get monthly revenue data for the last 12 months."""
    monthly_data = defaultdict(float)
    
    # Get date range for last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for order in orders:
        created_at = order.get("created_at")
        if isinstance(created_at, str):
            try:
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                continue
        else:
            date = created_at
            
        if start_date <= date <= end_date:
            month_key = date.strftime("%Y-%m")
            if order.get("delivery_status") == "delivered":
                monthly_data[month_key] += order_revenues.get(order["id"], 0)
    
    # Convert to list format and fill missing months with 0
    result = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        month_key = current_date.strftime("%Y-%m")
        result.append({
            "month": month_key,
            "revenue": round(monthly_data[month_key], 2)
        })
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return result[-12:]  # Return last 12 months

def get_top_selling_products(order_items, products):
    """Get top selling products based on quantity sold."""
    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    
    for item in order_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)
        subtotal = item.get("subtotal", 0)
        
        if product_id:
            product_sales[product_id]["quantity"] += quantity
            product_sales[product_id]["revenue"] += subtotal
    
    # Get product details and sort by quantity
    product_map = {p["id"]: p for p in products}
    top_products = []
    
    for product_id, sales in product_sales.items():
        if product_id in product_map:
            product = product_map[product_id]
            top_products.append({
                "id": product_id,
                "title": product.get("title"),
                "category": product.get("category"),
                "quantity_sold": sales["quantity"],
                "revenue": round(sales["revenue"], 2),
                "stock": product.get("stock", 0)
            })
    
    # Sort by quantity sold and return top 5
    top_products.sort(key=lambda x: x["quantity_sold"], reverse=True)
    return top_products[:5]

def get_recent_orders(orders, order_items):
    """Get recent orders with item details."""
    # Sort orders by created_at descending
    sorted_orders = sorted(orders, key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Group order items by order_id
    items_by_order = defaultdict(list)
    for item in order_items:
        items_by_order[item["order_id"]].append(item)
    
    recent_orders = []
    for order in sorted_orders[:10]:  # Last 10 orders
        order_id = order["id"]
        items = items_by_order.get(order_id, [])
        
        recent_orders.append({
            "id": order_id,
            "user_email": order.get("user_email"),
            "total_amount": order.get("total_amount"),
            "delivery_status": order.get("delivery_status"),
            "created_at": order.get("created_at"),
            "items_count": len(items),
            "items": items
        })
    
    return recent_orders

def get_order_analytics():
    """Get detailed order analytics with filtering options."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        status_filter = data.get("status_filter", "")
        date_from = data.get("date_from")
        date_to = data.get("date_to")
        
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get order items for this retailer
        order_items_response = supabase.table("order_items").select("*").eq("retailer_email", retailer_email).execute()
        order_items = order_items_response.data
        order_ids = list(set([item["order_id"] for item in order_items]))
        
        if not order_ids:
            return jsonify({"orders": [], "analytics": {}}), 200

        # Build query for orders
        orders_query = supabase.table("orders").select("*").in_("id", order_ids)
        
        # Apply filters
        if status_filter:
            orders_query = orders_query.eq("delivery_status", status_filter)
        
        if date_from:
            orders_query = orders_query.gte("created_at", date_from)
        
        if date_to:
            orders_query = orders_query.lte("created_at", date_to)
        
        orders_response = orders_query.order("created_at", desc=True).execute()
        filtered_orders = orders_response.data

        # Group order items by order_id
        items_by_order = defaultdict(list)
        for item in order_items:
            items_by_order[item["order_id"]].append(item)

        # Build filtered orders with items
        filtered_orders_with_items = []
        for order in filtered_orders:
            order_id = order["id"]
            order["items"] = items_by_order.get(order_id, [])
            filtered_orders_with_items.append(order)

        # Calculate analytics
        analytics = calculate_order_analytics(filtered_orders, order_items)

        return jsonify({
            "orders": filtered_orders_with_items,
            "analytics": analytics
        }), 200

    except Exception as e:
        print(f"Order analytics error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def calculate_order_analytics(orders, order_items):
    """Calculate analytics for filtered orders."""
    if not orders:
        return {
            "total_orders": 0,
            "total_revenue": 0,
            "average_order_value": 0,
            "status_breakdown": {}
        }
    
    total_orders = len(orders)
    
    # Calculate revenue for delivered orders only
    order_revenues = {}
    for item in order_items:
        order_id = item["order_id"]
        order_revenues[order_id] = order_revenues.get(order_id, 0) + item.get("subtotal", 0)
    
    delivered_revenue = sum(
        order_revenues.get(order["id"], 0) 
        for order in orders 
        if order.get("delivery_status") == "delivered"
    )
    
    average_order_value = delivered_revenue / total_orders if total_orders > 0 else 0
    
    # Status breakdown
    status_breakdown = {}
    for order in orders:
        status = order.get("delivery_status", "unknown")
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    return {
        "total_orders": total_orders,
        "total_revenue": round(delivered_revenue, 2),
        "average_order_value": round(average_order_value, 2),
        "status_breakdown": status_breakdown
    }

def get_product_analytics():
    """Get detailed product analytics."""
    try:
        data = request.get_json()
        auth_token = data.get("auth_token")
        
        if not auth_token:
            return jsonify({"error": "auth_token is required"}), 400

        retailer_email = verify_retailer_token(auth_token)
        if not retailer_email:
            return jsonify({"error": "Invalid auth_token"}), 401

        # Get products
        products_response = supabase.table("products").select("*").eq("retailer_email", retailer_email).execute()
        products = products_response.data
        
        if not products:
            return jsonify({
                "products": [],
                "analytics": {
                    "total_products": 0,
                    "low_stock_count": 0,
                    "out_of_stock_count": 0,
                    "category_breakdown": {},
                    "revenue_by_category": {}
                }
            }), 200

        # Get order items for sales data
        order_items_response = supabase.table("order_items").select("*").eq("retailer_email", retailer_email).execute()
        order_items = order_items_response.data

        # Calculate product analytics
        product_analytics = calculate_product_analytics(products, order_items)

        return jsonify({
            "products": products,
            "analytics": product_analytics
        }), 200

    except Exception as e:
        print(f"Product analytics error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def calculate_product_analytics(products, order_items):
    """Calculate analytics for products."""
    total_products = len(products)
    low_stock_count = sum(1 for p in products if 0 < p.get("stock", 0) < 10)
    out_of_stock_count = sum(1 for p in products if p.get("stock", 0) == 0)
    
    # Category breakdown
    category_breakdown = {}
    for product in products:
        category = product.get("category", "unknown")
        category_breakdown[category] = category_breakdown.get(category, 0) + 1
    
    # Revenue by category
    category_revenue = defaultdict(float)
    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    
    for item in order_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)
        subtotal = item.get("subtotal", 0)
        
        if product_id:
            product_sales[product_id]["quantity"] += quantity
            product_sales[product_id]["revenue"] += subtotal
    
    # Group revenue by category
    for product in products:
        product_id = product["id"]
        category = product.get("category", "unknown")
        if product_id in product_sales:
            category_revenue[category] += product_sales[product_id]["revenue"]
    
    return {
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "category_breakdown": category_breakdown,
        "revenue_by_category": dict(category_revenue)
    }