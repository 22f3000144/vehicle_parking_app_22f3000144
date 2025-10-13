# backend/api.py
from flask_restful import Api
from app import app               # use the app created in create_app()
from routes.user_routes import (
    ParkingListAPI,
    BookParkingAPI,
    ReleaseParkingAPI
)
# You can import more later:
# from routes.admin_routes import AdminDashboardAPI
# from routes.auth_routes import RegisterAPI, LoginAPI

# Initialize the API object
api = Api(app)

# ------------------------
# User routes
# ------------------------
api.add_resource(ParkingListAPI, "/api/parking/lots", endpoint="parking_lots")
api.add_resource(BookParkingAPI, "/api/parking/book", endpoint="book_parking")
api.add_resource(ReleaseParkingAPI, "/api/parking/release", endpoint="release_parking")

# ------------------------
# Example future routes
# ------------------------
# api.add_resource(AdminDashboardAPI, "/api/admin/dashboard", endpoint="admin_dashboard")
# api.add_resource(RegisterAPI, "/api/auth/register", endpoint="auth_register")
# api.add_resource(LoginAPI, "/api/auth/login", endpoint="auth_login")

print("✅ API routes registered successfully.")
