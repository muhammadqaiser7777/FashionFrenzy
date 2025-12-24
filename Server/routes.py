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

from controllers.admin.adminAuthController import adminLogin, adminLogout
# Initialize Blueprint
routes = Blueprint("routes", __name__)

# ===================== 🔐 Admin Authentication Routes =====================

# Authenticates admin credentials and generates token
routes.route("/admin/login", methods=["POST"])(adminLogin)

# Invalidates admin token to log out
routes.route("/admin/logout", methods=["POST"])(adminLogout)

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