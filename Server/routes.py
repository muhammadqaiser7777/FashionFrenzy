from flask import Blueprint # type: ignore # Blueprint for grouping all routes
# Importing controllers for various functionalities
from controllers.user.authController import signup, verify, login, logout
from controllers.user.passwordController import (
    change_password, password_forget, verify_identity, set_new_password
)
from controllers.user.otpController import otpRefresh, validate_otp

from controllers.retailer.retailerAuthController import retailerSignup, retailerVerify, retailerLogin, retailerLogout
from controllers.retailer.retailerPasswordController import (
    retailerChangePassword, retailerPasswordForget, retailerVerifyIdentity, retailerSetNewPassword
)
from controllers.retailer.retailerOtpController import retailerOtpRefresh, retailerValidateOtp
from controllers.retailer.productController import add_product, view_products, edit_product, delete_product
from controllers.retailer.orderController import view_orders, confirm_order, reject_order, dashboard

from controllers.admin.adminAuthController import adminLogin, adminLogout
from controllers.admin.productStatusController import view_pending_products, view_approved_products, view_rejected_products, edit_product_status
from controllers.admin.ordersStatusController import view_all_orders, edit_order_status, admin_dashboard
# Initialize Blueprint
routes = Blueprint("routes", __name__)

# ===================== 🔐 Admin Authentication Routes =====================

# Authenticates admin credentials and generates token
routes.route("/admin/login", methods=["POST"])(adminLogin)

# Invalidates admin token to log out
routes.route("/admin/logout", methods=["POST"])(adminLogout)

# ===================== 🔐 Admin Product Management Routes =====================

# View pending products
routes.route("/admin/view-pending-products", methods=["POST"])(view_pending_products)

# View approved products
routes.route("/admin/view-approved-products", methods=["POST"])(view_approved_products)

# View rejected products
routes.route("/admin/view-rejected-products", methods=["POST"])(view_rejected_products)

# Edit product status
routes.route("/admin/edit-product-status", methods=["POST"])(edit_product_status)

# ===================== 🔐 Admin Order Management Routes =====================

# View all orders
routes.route("/admin/view-all-orders", methods=["POST"])(view_all_orders)

# Edit order status
routes.route("/admin/edit-order-status", methods=["POST"])(edit_order_status)

# Get admin dashboard stats
routes.route("/admin/dashboard", methods=["POST"])(admin_dashboard)

# ===================== 🔐 User Authentication Routes =====================

# Handles user registration and stores user info
routes.route("/signup", methods=["POST"])(signup)

# Verifies OTP for newly signed-up users
routes.route("/verify", methods=["POST"])(verify)

# Authenticates user credentials and generates token
routes.route("/login", methods=["POST"])(login)

# Invalidates user token to log out
routes.route("/logout", methods=["POST"])(logout)

# ===================== 🔑 User Password Management Routes =====================

# Change password for logged-in users
routes.route("/change-password", methods=["POST"])(change_password)

# Initiates "forgot password" flow (sends OTP)
routes.route("/password-forget", methods=["POST"])(password_forget)

# Validates identity via OTP before setting new password
routes.route("/verify-identity", methods=["POST"])(verify_identity)

# Sets new password after verification
routes.route("/set-new-password", methods=["POST"])(set_new_password)

# ===================== 🔁 OTP Handling Routes =====================

# Refreshes and resends OTP
routes.route("/otp-refresh", methods=["POST"])(otpRefresh)

# Validates entered OTP against stored value
routes.route("/validate-otp", methods=["POST"])(validate_otp)




# ===================== 🔐 Retailer Authentication Routes =====================

# Handles retailer registration and stores retailer info
routes.route("/retailer/signup", methods=["POST"])(retailerSignup)

# Verifies OTP for newly signed-up retailers
routes.route("/retailer/verify", methods=["POST"])(retailerVerify)

# Authenticates retailer credentials and generates token
routes.route("/retailer/login", methods=["POST"])(retailerLogin)

# Invalidates retailer token to log out
routes.route("/retailer/logout", methods=["POST"])(retailerLogout)

# ===================== 🔑 Retailer Password Management Routes =====================

# Change password for logged-in retailers
routes.route("/retailer/change-password", methods=["POST"])(retailerChangePassword)

# Initiates "forgot password" flow (sends OTP)
routes.route("/retailer/password-forget", methods=["POST"])(retailerPasswordForget)

# Validates identity via OTP before setting new password
routes.route("/retailer/verify-identity", methods=["POST"])(retailerVerifyIdentity)

# Sets new password after verification
routes.route("/retailer/set-new-password", methods=["POST"])(retailerSetNewPassword)

# ===================== 🔁 OTP Handling Routes =====================

# Refreshes and resends OTP
routes.route("/retailer/otp-refresh", methods=["POST"])(retailerOtpRefresh)

# Validates entered OTP against stored value
routes.route("/retailer/validate-otp", methods=["POST"])(retailerValidateOtp)

# ===================== 🔐 Retailer Product Management Routes =====================

# Add a new product
routes.route("/retailer/add-product", methods=["POST"])(add_product)

# View existing products
routes.route("/retailer/view-products", methods=["POST"])(view_products)

# Edit a product
routes.route("/retailer/edit-product", methods=["POST"])(edit_product)

# Delete a product
routes.route("/retailer/delete-product", methods=["POST"])(delete_product)

# ===================== 🔐 Retailer Order Management Routes =====================

# View coming orders
routes.route("/retailer/view-orders", methods=["POST"])(view_orders)

# Confirm an order
routes.route("/retailer/confirm-order", methods=["POST"])(confirm_order)

# Reject an order
routes.route("/retailer/reject-order", methods=["POST"])(reject_order)

# Get dashboard stats
routes.route("/retailer/dashboard", methods=["POST"])(dashboard)