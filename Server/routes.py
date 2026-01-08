from flask import Blueprint, request, jsonify
from flask_cors import CORS

# ===================== Controllers =====================
from controllers.user.authController import signup, verify, login, logout
from controllers.user.passwordController import (
    change_password, password_forget, verify_identity, set_new_password
)
from controllers.user.otpController import otpRefresh, validate_otp
from controllers.user.viewProduct import view_top_products, get_product_by_id, search_products
from controllers.user.cartController import add_to_cart, remove_from_cart, view_cart
from controllers.user.orderController import place_order, view_orders

from controllers.retailer.retailerAuthController import (
    retailerSignup, retailerVerify, retailerLogin, retailerLogout
)
from controllers.retailer.retailerPasswordController import (
    retailerChangePassword, retailerPasswordForget,
    retailerVerifyIdentity, retailerSetNewPassword
)
from controllers.retailer.retailerOtpController import (
    retailerOtpRefresh, retailerValidateOtp
)
from controllers.retailer.productController import (
    add_product, view_products, edit_product, delete_product
)
from controllers.retailer.orderController import (
    view_orders, confirm_order, reject_order, dashboard
)
from controllers.retailer.advancedDashboardController import (
    get_advanced_dashboard_stats, get_order_analytics, get_product_analytics
)
from controllers.retailer.imageUploadController import (
    upload_product_image, delete_product_image, get_uploaded_images
)

from controllers.admin.adminAuthController import adminLogin, adminLogout
from controllers.admin.productStatusController import (
    view_pending_products, view_approved_products,
    view_rejected_products, edit_product_status
)
from controllers.admin.ordersStatusController import (
    view_all_orders, edit_order_status, admin_dashboard
)

# ===================== Blueprint =====================
routes = Blueprint("routes", __name__)

# 🔥 APPLY CORS TO BLUEPRINT (THIS WAS MISSING)
CORS(
    routes,
    supports_credentials=True,
    origins=[
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
)

# ===================== GLOBAL PREFLIGHT HANDLER =====================
@routes.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200

# ===================== 👤 USER ROUTES =====================
routes.route("/signup", methods=["POST", "OPTIONS"])(signup)
routes.route("/verify", methods=["POST", "OPTIONS"])(verify)
routes.route("/login", methods=["POST", "OPTIONS"])(login)
routes.route("/logout", methods=["POST", "OPTIONS"])(logout)

routes.route("/change-password", methods=["POST", "OPTIONS"])(change_password)
routes.route("/password-forget", methods=["POST", "OPTIONS"])(password_forget)
routes.route("/verify-identity", methods=["POST", "OPTIONS"])(verify_identity)
routes.route("/set-new-password", methods=["POST", "OPTIONS"])(set_new_password)

routes.route("/otp-refresh", methods=["POST", "OPTIONS"])(otpRefresh)
routes.route("/validate-otp", methods=["POST", "OPTIONS"])(validate_otp)

# ===================== 🔐 RETAILER ROUTES =====================
routes.route("/retailer/signup", methods=["POST", "OPTIONS"])(retailerSignup)
routes.route("/retailer/verify", methods=["POST", "OPTIONS"])(retailerVerify)
routes.route("/retailer/login", methods=["POST", "OPTIONS"])(retailerLogin)
routes.route("/retailer/logout", methods=["POST", "OPTIONS"])(retailerLogout)

routes.route("/retailer/change-password", methods=["POST", "OPTIONS"])(retailerChangePassword)
routes.route("/retailer/password-forget", methods=["POST", "OPTIONS"])(retailerPasswordForget)
routes.route("/retailer/verify-identity", methods=["POST", "OPTIONS"])(retailerVerifyIdentity)
routes.route("/retailer/set-new-password", methods=["POST", "OPTIONS"])(retailerSetNewPassword)

routes.route("/retailer/otp-refresh", methods=["POST", "OPTIONS"])(retailerOtpRefresh)
routes.route("/retailer/validate-otp", methods=["POST", "OPTIONS"])(retailerValidateOtp)

# ===================== 📦 RETAILER PRODUCTS & ORDERS =====================
routes.route("/retailer/add-product", methods=["POST", "OPTIONS"])(add_product)
routes.route("/retailer/view-products", methods=["POST", "OPTIONS"])(view_products)
routes.route("/retailer/edit-product", methods=["POST", "OPTIONS"])(edit_product)
routes.route("/retailer/delete-product", methods=["POST", "OPTIONS"])(delete_product)

routes.route("/retailer/view-orders", methods=["POST", "OPTIONS"])(view_orders)
routes.route("/retailer/confirm-order", methods=["POST", "OPTIONS"])(confirm_order)
routes.route("/retailer/reject-order", methods=["POST", "OPTIONS"])(reject_order)
routes.route("/retailer/dashboard", methods=["POST", "OPTIONS"])(dashboard)

# ===================== 🚀 ADVANCED DASHBOARD ROUTES =====================
routes.route("/retailer/dashboard/advanced-stats", methods=["POST", "OPTIONS"])(get_advanced_dashboard_stats)
routes.route("/retailer/orders/analytics", methods=["POST", "OPTIONS"])(get_order_analytics)
routes.route("/retailer/products/analytics", methods=["POST", "OPTIONS"])(get_product_analytics)

# ===================== 📸 IMAGE UPLOAD ROUTES =====================
routes.route("/retailer/upload-image", methods=["POST", "OPTIONS"])(upload_product_image)
routes.route("/retailer/delete-image", methods=["POST", "OPTIONS"])(delete_product_image)
routes.route("/retailer/images", methods=["POST", "OPTIONS"])(get_uploaded_images)

# ===================== ️ ADMIN ROUTES =====================
routes.route("/admin/login", methods=["POST", "OPTIONS"])(adminLogin)
routes.route("/admin/logout", methods=["POST", "OPTIONS"])(adminLogout)

routes.route("/admin/view-pending-products", methods=["POST", "OPTIONS"])(view_pending_products)
routes.route("/admin/view-approved-products", methods=["POST", "OPTIONS"])(view_approved_products)
routes.route("/admin/view-rejected-products", methods=["POST", "OPTIONS"])(view_rejected_products)
routes.route("/admin/edit-product-status", methods=["POST", "OPTIONS"])(edit_product_status)

routes.route("/admin/view-all-orders", methods=["POST", "OPTIONS"])(view_all_orders)
routes.route("/admin/edit-order-status", methods=["POST", "OPTIONS"])(edit_order_status)
routes.route("/admin/dashboard", methods=["POST", "OPTIONS"])(admin_dashboard)
